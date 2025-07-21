from utils.moduleListHandler import ModuleList, get_module_list
from utils.printers import print_error, print_warning, print_info, print_debug
from utils.config_info import Job
from utils.config_getters import (
    calculate_max_cpus,
    calculate_max_gpus,
    calculate_max_nodes,
    get_system_partition_details,
    get_valid_modes,
    get_valid_partitions,
    is_gpu_partition,
    get_min_nodes_for_cpus,
    is_valid_partition,
)
from utils.slurmifyValidationReport import SlurmifyValidationReport

validation_relaxed = True  # If true the script will continue even if there are errors


def validate_account(job: Job, report: SlurmifyValidationReport) -> bool:
    """Validates that the job has an account specified"""
    if job.system.resources.account is None:
        print_error(f"Error: Job {job.system.name} has no account specified")
        report.add_error(
            critical=True, errormsg=["No account specified"], info=["Not yet added"]
        )
        return False
    return True


def validate_gpu(
    job: Job, validation_info: dict, report: SlurmifyValidationReport
) -> bool:
    """Validates that the job's GPU request is within limits"""

    # Load the resources from the job
    gpu = job.system.resources.gpu
    mode = job.system.resources.mode
    partition = job.system.resources.partitions

    # Check that gpus is a number
    if not isinstance(gpu, int) and gpu is not None:
        print_error(f"Error: Job {job.name} requested {gpu} GPUs, must be a number")

        report.add_error(
            critical=True,
            errormsg=[f"Requested {gpu} GPUs, must be a number"],
        )
        return False

    if gpu is None or gpu == 0:
        # print_info("No GPU requested [ Valid ]")
        return True

    system_constraints = get_system_partition_details(partition, validation_info)

    if system_constraints is None:
        print_error(
            f"Error: Partition '{partition}' Missing system constraints. Contact admin"
        )

        report.add_error(
            critical=True,
            errormsg=[
                f"Partition '{partition}' missing system constraints. Contact admin"
            ],
        )

        return False

    if not is_gpu_partition(partition, validation_info):
        job.system.resources.partitions = "gpu"

    max_gpus = calculate_max_gpus(mode, validation_info)

    # print_info(f"The total number of gpus that can be used is: {max_gpus}")

    if gpu > max_gpus:
        print_error(f"Job {job.name} requested {gpu} GPUs, maximum is {max_gpus}")

        report.add_error(
            critical=True,
            errormsg=[f"Requested {gpu} GPUs, maximum is {max_gpus}"],
        )

        return False
    elif gpu < 1:
        print_error(f"Job {job.name} requested {gpu} GPUs, minimum is 1")
        print_error(f"Continuing with 1 GPUs")

        report.add_error(
            critical=False,
            errormsg=[f"Requested {gpu} GPUs, minimum is 1"],
            warning=["Continuing with 1 GPU"],
            info=[
                "To fix this issue, please specify a valid number of GPUs in the job configuration like this:",
                "  system=System(",
                "     resources=Resources(...",
                "       gpu=1)",
            ],
        )

        job.system.resources.gpu = 1
        return validation_relaxed

    return True


# TODO: Handle the case where multiple partitions are requested
def validate_partition(
    job: Job, validation_info: dict, report: SlurmifyValidationReport
) -> bool:
    """Validates that the job's partition is valid"""
    partition = job.system.resources.partitions
    gpus = job.system.resources.gpu

    if partition is None:
        partition = "cpu"

    if (
        gpus is not None
        and gpus > 0
        and not is_gpu_partition(partition, validation_info)
    ):
        print_debug(f"=============================================================")
        print_error(f"Partition '{partition}' does not support GPUs")
        print_warning(f"   Automatically switching to GPU partition")
        print_info(
            f"  -> Please specify a GPU partition in the job configuration like this:"
        )
        print_info(f"  -> system=System(")
        print_info(f"  ->   resources=Resources(...")
        print_info(f"  ->     partitions='gpu')")
        print_debug(f"=============================================================")

        report.add_error(
            critical=False,
            errormsg=["Partition does not support GPUs"],
            warning=["Automatically switched to GPU partition"],
            info=[
                "Please specify a GPU partition in the job configuration like this:",
                "    system=System(",
                "        resources=Resources(",
                "            ...",
                "            partitions='gpu'",
                "            ...",
                "        )",
                "    )",
            ],
        )

        partition = "gpu"

    if partition == "gpu" and (gpus == None or gpus == 0):
        print_error(f"Job {job.name} requested GPU partition but no GPUs")
        print_warning(f"Continuing with cpu partition")
        print_info(
            f"Please specify the number of GPUs in the job configuration like this:"
        )
        print_info(f"  system=System(")
        print_info(f"     resources=Resources(...")
        print_info(f"       gpu=1)")

        report.add_error(
            critical=False,
            errormsg=["Requested GPU partition but no GPUs"],
            warning=["Continuing with cpu partition"],
            info=[
                "Please specify the number of GPUs in the job configuration like this:\n"
                "   system=System(",
                "       resources=Resources(...,gpu=1,...))",
            ],
        )

        partition = "cpu"

    job.system.resources.partitions = partition

    valid_partitions = get_valid_partitions(validation_info)

    if not is_valid_partition(partition, validation_info):
        print_error(f"Job {job.name} requested invalid partition '{partition}'")
        print_info(f"    Valid partitions are: {', '.join(valid_partitions)}")
        print_warning(f"    Automatically switching to cpu partition for now")

        report.add_error(
            critical=False,
            errormsg=[f"Requested invalid partition {partition}"],
            warning=["Automatically switched to cpu partition"],
            info=[f"Valid partitions are: {', '.join(valid_partitions)}"],
        )

        job.system.resources.partitions = "cpu"
        print_debug("-------------------------------------------------------------")

        return validation_relaxed

    return True


def validate_nodes(
    job: Job, validation_info: dict, report: SlurmifyValidationReport
) -> bool:
    """Validates that the job's node count is within limits"""
    nodes = job.system.resources.nodes
    mode = job.system.resources.mode
    ntasks = job.system.resources.ntasks
    partition = job.system.resources.partitions

    if nodes is None:
        nodes = 1
        job.system.resources.nodes = nodes
        print_warning(f"Job {job.name} has no nodes specified")

    # Check that node is a number This sould be already handled now MAYBE REMOVE
    if not isinstance(nodes, int):
        print_error(f"Error: Job {job.name} requested {nodes} nodes, must be a number")
        report.add_error(
            critical=True,
            errormsg=[f"Requested {nodes} nodes, must be a number"],
        )
        return False

    # TODO: This is not how it works 1 task can only be run on one node
    # TODO: Need to use ntasks for mpi for example to use more cpus
    min_nodes = get_min_nodes_for_cpus(
        job.system.resources.cores, partition, ntasks, validation_info
    )

    if nodes < min_nodes:
        print_error(f"Job {job.name} requested {nodes} nodes, minimum is {min_nodes}")
        print_warning(f"Continuing with {min_nodes} nodes")

        report.add_error(
            critical=False,
            errormsg=[f"Requested {nodes} nodes, minimum is {min_nodes}"],
            warning=[f"Continuing with {min_nodes} nodes"],
        )

        job.system.resources.nodes = min_nodes
        nodes = min_nodes

    max_nodes = calculate_max_nodes(mode, partition, validation_info)

    if nodes > ntasks:
        print_error(f"Job {job.name} requested {nodes} nodes, but ntasks is {ntasks}")
        print_warning(f"Continuing with {ntasks} nodes")

        report.add_error(
            critical=False,
            errormsg=[f"Requested {nodes} nodes, but ntasks is {ntasks}"],
            warning=[f"Continuing with {ntasks} nodes"],
        )

        job.system.resources.nodes = ntasks
        nodes = ntasks

    if nodes > max_nodes:
        print_error(f"Job {job.name} requested {nodes} nodes, maximum is {max_nodes}")
        report.add_error(
            critical=True,
            errormsg=[f"Requested {nodes} nodes, maximum is {max_nodes}"],
            info=[
                f"To fix this issue, please specify a valid number of nodes in the job configuration like this:",
                f"  system=System(",
                f"     resources=Resources(...",
                f"       nodes=1)",
            ],
        )
        return False
    elif nodes < 1:
        print_error(f"Job {job.name} requested {nodes} nodes, minimum is 1")
        print_warning(f"Continuing with 1 node")

        report.add_error(
            critical=False,
            errormsg=[f"Requested {nodes} nodes, minimum is 1"],
            warning=[f"Continuing with 1 node"],
            info=[
                f"To fix this issue, please specify a valid number of nodes in the job configuration like this:",
                f"  system=System(",
                f"     resources=Resources(...",
                f"       nodes=1)",
            ],
        )

        job.system.resources.nodes = 1
        return validation_relaxed
    return True


def validate_mode(
    job: Job, validation_info: dict, report: SlurmifyValidationReport
) -> bool:
    """Validates that the job's QOS mode is valid"""
    mode = job.system.resources.mode
    valid_modes = get_valid_modes(validation_info)

    if mode is None:
        mode = "default"

    if mode not in valid_modes:
        print_debug(f"==============================================================")
        print_error(f"Job {job.system.name} requested invalid mode '{mode}'")

        print_warning(f"Automatically switching to default mode")
        print_info(f"Valid modes are: {', '.join(valid_modes)}")

        ## Tell the user how and where to change
        print_info(f"Please specify a valid mode in the job configuration like this:")
        print_info(f"  system=System(")
        print_info(f"     resources=Resources(...")
        print_info(f"       mode='default')")

        print_debug(f"==============================================================")

        report.add_error(
            critical=False,
            errormsg=[f"Requested invalid mode: {mode}"],
            warning=["Automatically switched to default mode"],
            info=[
                f"Valid modes are: {', '.join(valid_modes)}",
                "Please specify a valid mode in the job configuration like this:",
                "   system=System(",
                "       resources=Resources(",
                "           mode='default'",
                "       )",
                "    )",
            ],
        )

        job.system.resources.mode = "default"
        return validation_relaxed
    return True


def parse_time_to_seconds(time_str: str) -> int:
    """
    Parse different SLURM time formats and convert to seconds
    Supported formats:
    - M (minutes)
    - M:S (minutes:seconds)
    - H:M:S (hours:minutes:seconds)
    - D-H (days:hours)
    - D-H:M (days:hours:minutes)
    - D-H:M:S (days:hours:minutes:seconds)
    """
    try:
        # Check if it's just minutes (single integer)
        if time_str.isdigit():
            return int(time_str) * 60

        # Check if it contains days (D-H format)
        if "-" in time_str:
            days_part, time_part = time_str.split("-")
            days = int(days_part)

            # Handle different time part formats after the day
            time_components = time_part.split(":")

            if len(time_components) == 1:  # D-H format
                hours = int(time_components[0])
                return (days * 24 * 3600) + (hours * 3600)
            elif len(time_components) == 2:  # D-H:M format
                hours, minutes = map(int, time_components)
                return (days * 24 * 3600) + (hours * 3600) + (minutes * 60)
            elif len(time_components) == 3:  # D-H:M:S format
                hours, minutes, seconds = map(int, time_components)
                return (days * 24 * 3600) + (hours * 3600) + (minutes * 60) + seconds

        # Handle time formats without days
        time_components = time_str.split(":")

        if len(time_components) == 2:  # M:S format
            minutes, seconds = map(int, time_components)
            return (minutes * 60) + seconds
        elif len(time_components) == 3:  # H:M:S format
            hours, minutes, seconds = map(int, time_components)
            return (hours * 3600) + (minutes * 60) + seconds

        raise ValueError(f"Unrecognized time format: {time_str}")

    except Exception as e:
        raise ValueError(f"Error parsing time '{time_str}': {str(e)}")


def validate_time(
    job: Job, validation_info: dict, report: SlurmifyValidationReport
) -> bool:
    """Validates that the job's runtime is valid for its QOS mode"""
    time = job.system.resources.time
    mode = job.system.resources.mode

    if time is None:
        time = "00:15:00"
        job.system.resources.time = time

    if mode is None:
        mode = "default"
        job.system.resources.mode = mode

    constraints = validation_info["constraints"]["time"]

    if mode in constraints:
        max_time_str = constraints[mode]

        try:
            # Convert both times to seconds for comparison
            requested_seconds = parse_time_to_seconds(time)
            max_seconds = parse_time_to_seconds(max_time_str)

            if requested_seconds > max_seconds:
                print_error(
                    f"Error: Job {job.name} requested {time} runtime in '{mode}' mode"
                )
                print_error(f"Maximum time for '{mode}' is {max_time_str}")

                report.add_error(
                    critical=True,
                    errormsg=[f"Requested {time} runtime in '{mode}' mode"],
                    warning=[f"Maximum time for '{mode}' is {max_time_str}"],
                )

                return False

        except ValueError as e:
            print_error(f"Error validating time: {str(e)}")

            report.add_error(
                critical=True,
                errormsg=[f"Error validating time: {str(e)}"],
            )

            return False

    return True


def validate_cpus(
    job: Job, validation_info: dict, report: SlurmifyValidationReport
) -> bool:
    cpus_per_task: int = job.system.resources.cores
    mode = job.system.resources.mode
    partition = job.system.resources.partitions
    ntasks = job.system.resources.ntasks
    nodes = job.system.resources.nodes

    max_cpus = calculate_max_cpus(
        cpus_per_task, partition, nodes, ntasks, validation_info, report
    )

    if max_cpus == None:
        print_error(
            f"Error: The selected amount of cpus is not possible with the current configuration"
        )

        return False
    return True


def validate_ntasks(job: Job, report: SlurmifyValidationReport) -> bool:
    # Ntasks is the number of tasks that will be run on the node if 2 ntasks is
    # specified but 1 node the total amount of cores will double and so needs to be checked

    if job.system.resources.ntasks is None:
        print_error(f"Error: Job {job.name} has no ntasks specified")
        print_error(f"Continuing with 1 ntask")

        report.add_error(
            critical=False,
            errormsg=["No ntasks specified"],
            warning=["Continuing with 1 ntask"],
        )

        job.system.resources.ntasks = 1
        return validation_relaxed

    # check if is a nuber and is greater than 0
    if (
        not isinstance(job.system.resources.ntasks, int)
        or job.system.resources.ntasks < 1
    ):
        print_error(f"Error: Job {job.name} has invalid ntasks specified")
        print_error(f"Continuing with 1 ntask")

        report.add_error(
            critical=False,
            errormsg=["Invalid ntasks specified"],
            warning=["Continuing with 1 ntask"],
        )

        job.system.resources.ntasks = 1
        return validation_relaxed

    return True


def validate_system(
    job: Job, validation_info: dict, report: SlurmifyValidationReport
) -> bool:
    """Main validation function that calls specialized validators"""
    print_debug("#################################################################")
    print_debug("\n")

    print_info("-------------------------------------------------------------")
    print_info("Validating System")
    print_info(("Job: ", job.name))
    print_info("-------------------------------------------------------------")

    # List of all validators
    # Account validation is not performed
    validators = [
        lambda j, v, r: validate_account(j, r),  # GOOD
        lambda j, v, r: validate_partition(j, v, r),  # GOOD
        lambda j, v, r: validate_mode(j, v, r),  # GOOD
        lambda j, v, r: validate_ntasks(j, r),  # GOOD
        lambda j, v, r: validate_nodes(j, v, r),  # GOOD (Check if works with gpu)
        lambda j, v, r: validate_gpu(
            j, v, r
        ),  # Nearly done (Need to check --gpus-per-task)
        lambda j, v, r: validate_cpus(j, v, r),  # GOOD
        lambda j, v, r: validate_time(j, v, r),  # GOOD
    ]
    # Run all validators and collect results
    results = [validator(job, validation_info, report) for validator in validators]

    result = all(results)
    print_debug("\n")
    print_debug("\n")
    if not result:
        print_error("System Validation Failed")
    else:
        print_info("System Validation Passed")
    print_debug("\n")
    print_debug("END OF VALIDATION")
    print_debug("#################################################################")
    # Return True only if all validations passed
    return result


def validate_modules(job: Job, report: SlurmifyValidationReport) -> bool:
    """
    This function checks if the requested modules are available in the system.
    """
    if job.modules is None:
        return True

    requested_modules = job.modules.get_modules()
    module_list: ModuleList = get_module_list()

    module_names = module_list.get_modules()

    for module in requested_modules:
        print_debug(f"Checking module: {module}")

        # Module names have a specific format, ToolName/Version
        # There are a few that are a little different like env/smth/version

        # Decompose the module name into its components
        try:
            split = module.name.split("/")
            moduleName = split[0]
            moduleVersion = split[1] if len(split) > 1 else None
            environment = split[2] if len(split) > 2 else None

            if moduleName not in module_names:
                print_error(f"Module name '{moduleName}' is not valid")
                # print_error(f"Available modules are: {', '.join(module_names)}")

                search_module = module_list.search_modules_with_versions(moduleName)

                if search_module is None:
                    report.add_error(
                        critical=True,
                        errormsg=[f"Module name '{moduleName}' is not valid"],
                        info=[
                            f"No similar modules found.",
                        ],
                    )
                    return False

                report.add_error(
                    critical=True,
                    errormsg=[f"Module name '{moduleName}' is not valid"],
                    info=[
                        # f"Available modules are: {', '.join(module_names)}",
                        f"Did you mean: {', '.join(search_module)}"
                    ],
                )

                return False

            available_versions = module_list.get_module_versions(moduleName)
            if moduleVersion not in available_versions:
                print_error(f"Module version '{moduleVersion}' is not valid")
                report.add_error(
                    critical=True,
                    errormsg=[f"Module version '{moduleVersion}' is not valid"],
                    info=[
                        f"Available versions for '{moduleName}': {', '.join(available_versions)}"
                    ],
                )

                return False

            ## TODO: ENVIRONEMTS env are currently boken since the module list generator doesnt take them into account so they dont exist in the list !!!

        except Exception as e:
            print_error(f"Error: {e}")
            print_error(f"Module name '{module}' is not valid")
            return False

        # Check if the module name is valid
        print_debug(f"Module name: {moduleName}")
        print_debug(f"Module version: {moduleVersion}")
        print_debug(f"Module environment: {environment}")

    return True


def validate_logs(job: Job) -> bool:
    return True


def validate_environment(job: Job) -> bool:
    return True
