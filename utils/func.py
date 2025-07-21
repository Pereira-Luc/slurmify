from utils.config_getters import load_config
from utils.config_info import Job, Jobs
from utils.moduleListHandler import get_module_list
from utils.printers import print_debug, print_info, print_warning, print_error
from utils.slurmifyValidationReport import SlurmifyValidationReport
from utils.validators import (
    validate_system,
    validate_logs,
    validate_modules,
    validate_environment,
)
from types import ModuleType
import os
import requests

"""
This function will be used to validate the job configuration before anything else.

:param job: cfg.Job
:return: bool


TODO:   
    Things that I want to validate not necessary all in this function
        -   Validate that the system that was requested is possible number of cores and so on (Mostly done)
    
        -   Maybe it is possible to validate the environment variables not sure though
            but checking that they don't do errors should be possible (Not sure if it is worth it)
            
        -   Verify the existence of the modules that are requested (function exists but the list is not complete)
            This should be able to be done with module avail or something similar
            
        -   TODO: Check that the logs are valid paths other then that I don't think there is much to do
        
        -   Check that the exec_command is valid ???? not sure if this Is possible and need to be 
            checked how and what commands
"""


"""
@deprecated

    startswith("_") is used to ignore the private attributes of the class but current classes have no private attributes 
    (Maybe remove or keep for future use)

"""
skip_modules: bool = False


def set_skip_modules(skip: bool):
    """
    Set whether to skip module validation.

    Args:
        skip (bool): If True, skip module validation.
    """
    global skip_modules
    skip_modules = skip
    if skip_modules:
        print_warning("Skipping module validation")


def start_validation(Jobs: list[Job]):
    error_reports: list[SlurmifyValidationReport] = []
    for job in Jobs:
        valid, error_report = validate_job(job)
        error_reports.append(error_report)
    return error_reports


def get_slurmify_jobs(
    module: ModuleType, error_report: SlurmifyValidationReport
) -> bool | list[Job]:
    """
    Get the jobs from the module.

    Args:
        module (ModuleType): The loaded Python module.
        error_report (SlurmifyValidationReport): The validation report for the module.
        valid (bool): Whether the module is valid or not.


    Returns:
        bool: True if the module is valid, False otherwise.
        list[Job]: A list of jobs from the module.
    """

    jobs: list[Job] = []

    # There should be not error_report because it's after validation
    if error_report is not None:
        return False

    # Ensure module was loaded successfully
    if module is None:
        print_warning("Module is None")
        return False

    # Get jobs from the configuration
    try:
        allJobs: Jobs = module.Jobs
        jobs: list[Job] = (
            allJobs.get_jobs()
        )  # List of the jobs from the configuration file
    except AttributeError:
        return False
    except Exception as e:
        return False

    return jobs


def validate_job(
    job: Job, systemConfigPath: str = "systemConfig/conf.yaml"
) -> tuple[bool, SlurmifyValidationReport]:
    config: dict = load_config()
    constraints: dict = config["constraints"]
    system_constraints: dict = config["system_constraints"]
    job_validity_report: SlurmifyValidationReport = SlurmifyValidationReport(
        job.name, job
    )

    all_constraints = {
        "constraints": constraints,
        "system_constraints": system_constraints,
    }

    result = check_job_validity(job, all_constraints, job_validity_report)

    return result, job_validity_report


# TODO: There is no validation for FPGA cards
# TODO: There is no validation for space constraints
def check_job_validity(
    job: Job, validation_info: dict, report: SlurmifyValidationReport
) -> bool:
    """Main validation function that calls specialized validators"""

    if not validate_system(job, validation_info, report):
        return False

    if not validate_logs(job):
        return False

    if not skip_modules:
        if not validate_modules(job, report):
            return False

    if not validate_environment(job):
        return False

    return True

    """
    This function will be used to generate the slurm script that will be used to run the job.
    """


def generate_slurm_system_script(job: Job, slurm_translation: dict) -> str:
    # Create an attractive ASCII header
    slurm = """
#==============================================================================#
#                                                                              #
#                         SLURM JOB CONFIGURATION                              #
#                                                                              #
#==============================================================================#
"""
    # Add job name with nice formatting
    slurm += f"\n#SBATCH --job-name={job.name}"

    # Add a separator for resource section
    slurm += """
#------------------------------------------------------------------------------#
#                           RESOURCE CONFIGURATION                             #
#------------------------------------------------------------------------------#
"""

    # Add resources with proper formatting
    resources_dict: dict[str, Any] = vars(job.system.resources)

    for attr_name, value in resources_dict.items():
        if attr_name.startswith("_"):
            continue
        if value is None:
            continue
        if value == 0:
            continue
        slurm_option = slurm_translation.get(attr_name)
        if slurm_option:
            slurm += f"\n#SBATCH --{slurm_option}={value}"
        else:
            print_warning(f"Warning: No SLURM translation for '{attr_name}'")
            print_warning(f"         Using '{attr_name}' as SLURM option")
            print_warning(f"         Please check the SLURM documentation")
            print_warning(f"         to ensure this is a valid option")
            print_warning(f"         use at your own risk!")
            slurm += f"\n#SBATCH --{attr_name}={value}"  # TODO: Ask user if he want to add it or just skip
            pass

    if not job.logs == None:  # logs are not required will be handled by slurm

        # Add a separator for log section
        slurm += """
#------------------------------------------------------------------------------#
#                               LOG SETTINGS                                   #
#------------------------------------------------------------------------------#
"""

        # Add log configuration
        log_dict: dict[str, Any] = vars(job.logs)

        for attr_name, value in log_dict.items():
            if attr_name.startswith("_"):
                continue
            if value is None:
                continue
            logs_options = slurm_translation.get(f"logs")
            if logs_options is None:
                print_warning(f"Warning: No SLURM translation for '{attr_name}'")
                print_warning(f"         Using '{attr_name}' as SLURM option")
                print_warning(f"         Please check the SLURM documentation")
                print_warning(f"         to ensure this is a valid option")
                print_warning(f"         use at your own risk!")

            # get logs from logs_options
            slurm_option = logs_options.get(attr_name)
            if slurm_option is None:
                print_warning(f"Warning: No SLURM translation for '{attr_name}'")
                print_warning(f"         Using '{attr_name}' as SLURM option")
                print_warning(f"         Please check the SLURM documentation")
                print_warning(f"         to ensure this is a valid option")
                print_warning(f"         use at your own risk!")
                slurm_option = attr_name
            # print(f"Log option: {slurm_option} = {value}")
            print_debug(f"Log option: {slurm_option} = {value}")
            if slurm_option:
                slurm += f"\n#SBATCH --{slurm_option}={value}"
            else:
                # slurm += f"\n#SBATCH --{attr_name}={value}"
                pass
    return slurm


def generate_slurm_env_script(job: Job) -> str:
    slurm = """
#==============================================================================#
#                           ENVIRONMENT SETUP                                  #
#==============================================================================#
"""
    if job.environments is None:
        return ""
    for env in job.environments:
        slurm += f"\n# {env.name} environment"
        for command in env.commands:
            slurm += f"\n{command}"
    return slurm


def generate_slurm_module_script(job: Job) -> str:
    slurm = """
#==============================================================================#
#                            MODULE LOADING                                    #
#==============================================================================#
"""
    if not job.modules is None:
        for module in job.modules.get_modules():
            slurm += f"\nmodule load {module.name}"
        return slurm
    return ""


def generate_slurm_exec_script(job: Job) -> str:
    slurm = """
#==============================================================================#
#                           EXECUTION COMMAND                                  #
#==============================================================================#
"""
    if type(job.exec_command) == str:
        return f"\n{job.exec_command}"

    for command in job.exec_command:
        slurm += f"\n{command}"

    return slurm


def generate_slurm_script(
    job: Job,
    config_path: str = None,
    create_file: bool = True,
    output_path: str = "./out",
) -> str:

    if config_path is None:
        # Default to the generator config
        config = load_config()

    slurm_translation = config["SlurmInfo"]
    slurm: str = "#!/bin/bash -l"

    print_info("Generating SLURM script...")

    # get all the resources
    slurm += generate_slurm_system_script(job, slurm_translation)
    slurm += generate_slurm_env_script(job)
    slurm += generate_slurm_module_script(job)
    slurm += generate_slurm_exec_script(job)

    if not create_file:
        return slurm

    # print(slurm)

    # Write the slurm script to a file ./out/job_name.sbatch

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    file_path = os.path.join(
        output_path, f"{job.name}.sh"
    )  # TODO: Make this dynamic and not hardcoded

    with open(file_path, "w") as file:
        file.write(slurm)

    print_debug(f"SLURM script generated for {job.name}")
    return file_path


def generate_slurm_script_from_config(
    list_of_job: list[Job], valid: bool = False, output_path: str = "./out"
):
    """Generate a slurm script from a slurmify config file

    IMPORTANT: This function should only be used after validation of the config file.

    Args:
        slurmify_config_path (str): Path to the slurmify config file

    Returns:
        str | None: Path to the generated slurm script or None if failed
    """
    if not valid:
        print_error("Slurmify config file is not valid | Should never happen")
        return None

    sbatch_paths: list[str] = []

    for job in list_of_job:
        sbatch_path: str = generate_slurm_script(
            job, create_file=True, output_path=output_path
        )
        sbatch_paths.append(sbatch_path)

    return sbatch_paths


def search_module(name: str) -> list[str]:
    """
    This function is used to search for a module in the system.
    Args:
        module_name (str): The name of the module to search for.
    Returns:
        list[str]: A list of module names that match the search query.
    """
    module_list = get_module_list()
    if module_list is None:
        print_error("Module list is None")
        return []

    # Search for the module in the module list
    search_results: list[str] = module_list.search_modules_with_versions(name)
    if not search_results:
        print_warning(f"No modules found for '{name}'")
        return []

    print_info(f"Found {len(search_results)} modules for '{name}':")

    return search_results


# Not Finished
def submit_slurm_job(jwt_token: str, workdir: str, job: Job, slurm: str = None):
    """
    Submit the Slurm job to the cluster.

    Documentation: https://docs.lxp.lu/web_services/slurmrestd/#__tabbed_5_2

    Args:
        jwt_token (str): The JWT token for authentication.
        workdir (str): The working directory for the job.
        job (Job): The job object containing job details.
        slurm (str): The Slurm script to be submitted. # Maybe generate it here instead of passing it
    """
    print("Submitting job...")  # TODO: Add error message here
    if jwt_token is None:
        return False, ""
    if job is None:
        return False, ""

    SLURM_URL = "https://slurm.cloud.lxp.lu"
    API_VER = "v0.0.40"
    SLURM_JWT = jwt_token
    USER_NAME = "lcpereira"
    ACCOUNT = job.system.resources.account

    # print(slurm)
    print(workdir)
    print(job)

    response = requests.post(
        f"{SLURM_URL}/slurm/{API_VER}/job/submit",
        headers={
            "X-SLURM-USER-NAME": f"{USER_NAME}",
            "X-SLURM-USER-TOKEN": f"{SLURM_JWT}",
        },
        json={
            "script": f"{slurm}",
            "job": {
                "name": f"{job.name}",
                "qos": f"{job.system.resources.mode}",
                "partition": f"{job.system.resources.partitions}",
                "time_limit": 20,
                "nodes": f"{job.system.resources.nodes}",
                "account": f"{ACCOUNT}",
                "cpus_per_task": job.system.resources.cores,
                # "nodes": job.system.resources.nodes,
                "tasks": job.system.resources.ntasks,
                # "ntasks": job.system.resources.ntasks,
                "standard_error": f"{job.logs.error}",
                "standard_output": f"{job.logs.default}",
                # "current_working_directory": f"{st.session_state.workdir}",
                "environment": [f"USER={USER_NAME}"],
            },
        },
    )

    response.raise_for_status()

    if response.json().get("job_id") is None:
        return False, ""

    job_id = response.json().get("job_id")
    print(f"Job submitted with ID: {job_id}")
    return True, job_id
