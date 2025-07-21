import re
import os
import time
import yaml
from utils import arg_handler
from utils.config_info import Job, Jobs
from utils.func import (
    generate_slurm_script_from_config,
    get_slurmify_jobs,
    search_module,
    set_skip_modules,
    start_validation,
    generate_slurm_script,
)
from utils.printers import print_error, print_success, print_info, enable_printing
import subprocess
import argparse
from utils.slurmifyLoader import load_python_conf_file
from utils.slurmifyValidationReport import SlurmifyValidationReport
from utils.arg_handler import arg_handler
import utils.colors as COLOR_MAP


testing_mode = False
auto_run_slurm = False
# If this is true it will invalidate the slurmify if there is any error and not
# Automaticaly fix it Not used rn
strict_mode = True


def validate_slurmify_config(
    path: str, generate_slurm: bool = False
) -> tuple[bool, list[SlurmifyValidationReport]]:
    """Validate the SLURM configuration file:
    Each Job will have its own validation report

    Args:
        path (str): Path to the SLURM configuration file
    """

    print_info(f"Validating SLURM configuration file: {path}")

    reports: list[SlurmifyValidationReport] = []

    # Load the Python configuration file
    module, error_report = load_python_conf_file(path)

    if module is None:
        reports.append(error_report)
        print_error("Configuration file is not valid")
        return False, reports

    # Get the jobs from the module
    jobs: list[Job] = get_slurmify_jobs(module, error_report)

    if not jobs:
        reports.append(error_report)
        print_error("No jobs found in the configuration file")
        return False, reports

    # Validate the jobs
    reports: list[SlurmifyValidationReport] = start_validation(jobs)

    invalid_job = False
    for report in reports:

        if not report.valid:
            invalid_job = True
            print_error(f"Job {report.job_name} is not valid")
            # print_error(report.error_report)

    if invalid_job:
        return False, reports

    print_success("SLURM configuration file is valid")
    return True, reports


def testing_configs(prefix: str, auto_run_slurm: bool = False) -> None:
    """
    This function is used to test a mutitude of configurations to testt if the tests are
    working correctly and if the slurm scripts are generated correctly.

    The folder Structure is as follows:
        - TypeOfTest1
            - Test1-n.py
        - TypeOfTest2
            - Test1-n.py

    args:
        prefix: The prefix of the folder to test. This is used to find the folder to test.
        auto_run_slurm: If True it will run the slurm script and check if it runs correctly.
    """

    print_info("Starting testing configs")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    tests_information = os.path.join(current_dir, "TestConfigs", "TestInfo.yaml")
    tests_path = os.path.join(current_dir, prefix)

    with open(tests_information, "r") as file:
        tests_info = yaml.safe_load(file)

    print_info(f"Tests information: {tests_info}")

    top_layer_folders = os.listdir(tests_path)

    for folder in top_layer_folders:
        testing_folder = tests_path + folder + "/"

        if not os.path.isdir(testing_folder):
            continue

        amount_of_tests = len(
            [
                f for f in os.listdir(testing_folder) if f.endswith(".py")
            ]  # Filter py files because of cache files
        )
        amount_of_failed_tests = 0
        amount_of_passed_tests = 0
        amount_of_skipped_tests = 0

        l1 = re.sub(r"[^a-zA-Z0-9]", "", prefix)
        l2 = folder
        l3 = "tests"

        print("==" * 50)

        test_description = tests_info.get(l1, {}).get(l2, {}).get("description", None)

        print(
            f"{COLOR_MAP.YELLOW}Testing folder: {testing_folder} {test_description} {COLOR_MAP.RESET}"
        )
        no_info_tests = []

        for tests in os.listdir(testing_folder):
            if not tests.endswith(".py"):
                continue

            test_path = testing_folder + tests
            valid, error_reports = validate_slurmify_config(test_path)

            tested_jobs: list[Job] = (
                []
            )  # List of jobs inside of the file reaired becquse it is possible to have multiple jobs in the same file

            for report in error_reports:
                if report.valid:
                    tested_jobs.append(
                        report.job
                    )  # Add the validated Job to the list for generation
                    continue

                tested_jobs.append(report.job)

            l4 = tests

            validation_information = (
                tests_info.get(l1, {}).get(l2, {}).get(l3, {}).get(l4, None)
            )

            if validation_information is None:
                if not valid:
                    no_info_tests.append(
                        f"{COLOR_MAP.RED}Config File: {tests} is {valid} {COLOR_MAP.RESET}"
                    )
                else:
                    no_info_tests.append(
                        f"{COLOR_MAP.GREEN}Config File: {tests} is {valid} {COLOR_MAP.RESET}"
                    )

                amount_of_skipped_tests += 1
                continue

            expected_result = validation_information.get("expected_result", None)

            if expected_result == "valid":
                expected_result = True
            elif expected_result == "invalid":
                expected_result = False

            message = ""

            if valid != expected_result:
                message = f"{COLOR_MAP.RED}[Test failed] {tests} {validation_information.get('description', None)} {COLOR_MAP.RESET}"
                amount_of_failed_tests += 1
            else:
                message = f"{COLOR_MAP.GREEN}[Test passed] {tests} {validation_information.get('description', None)} {COLOR_MAP.RESET}"
                amount_of_passed_tests += 1

            if not auto_run_slurm or not valid:
                print(message)
                continue

            # Check if Slurm is available using sinfo
            try:
                result = subprocess.run(["sinfo"], capture_output=True, text=True)
            except FileNotFoundError:
                message += f"{COLOR_MAP.RED}| Slurm [UNAVAILABE]{COLOR_MAP.RESET}"
                print(message)
                print_error("Slurm is not available")
                continue

            tmp_test_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "tmpTest"
            )

            # TODO: And need to remove the fila after the test
            # Generate a TEMP SLURM script file to be executed by SLURM --test-onlyy
            sbatch_paths = generate_slurm_script_from_config(
                tested_jobs, valid=valid, output_path=tmp_test_path
            )

            if sbatch_paths is None:
                continue

            for sbatch in sbatch_paths:
                # Run the slurm script and check if it runs correctly
                if sbatch.endswith(".sh"):
                    output = subprocess.run(
                        ["sbatch", "--test-only", sbatch],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )

                job_id = None

                if output.stderr:
                    print_error(f"output: {output.stderr.decode('utf-8')}")

                    match = re.search(r"Job (\d+)", output.stderr.decode("utf-8"))

                    if match:
                        job_id = match.group(1)

                if job_id is None:
                    message += f"{COLOR_MAP.RED}| Slurm [FAILED] {COLOR_MAP.RESET}"
                    print_error("Slurm script failed to run")
                    amount_of_failed_tests += 1
                    continue

                message += f"{COLOR_MAP.GREEN}| Slurm [PASSED] {COLOR_MAP.RESET}"
                print_success("Slurm script passed to run")

            print(message)

        print(f"{COLOR_MAP.YELLOW}Other Configs {COLOR_MAP.RESET}")
        for no_info_test in no_info_tests:
            print(no_info_test)

        print(" ")
        print(
            f"Total: {amount_of_tests}, Passed: {amount_of_passed_tests} ({(amount_of_passed_tests / amount_of_tests) * 100:.1f}%), "
            f"Failed: {amount_of_failed_tests} ({(amount_of_failed_tests / amount_of_tests) * 100:.1f}%), "
            f"Skipped: {amount_of_skipped_tests} ({(amount_of_skipped_tests / amount_of_tests) * 100:.1f}%) {COLOR_MAP.RESET}"
        )


def generate_slurm_script_from_args(args: argparse.Namespace) -> None:
    """Generate a SLURM script based on command line arguments"""

    partition = args.partition
    cores = args.cores
    nodes = args.nodes
    ntasks = args.ntasks
    gpu = args.gpu
    qos = args.qos
    time = args.time
    command = args.command
    logs_default = args.logs_default
    logs_error = args.logs_error
    envs = args.env
    modules = args.module

    print_info("Generating SLURM script with the following parameters:")
    print_info(f"Partition: {partition}")
    print_info(f"Cores: {cores}")
    print_info(f"Nodes: {nodes}")
    print_info(f"Tasks: {ntasks}")
    print_info(f"GPUs: {gpu}")
    print_info(f"QOS: {qos}")
    print_info(f"Time: {time}")
    print_info(f"Command: {command}")
    print_info(f"Logs default: {logs_default}")
    print_info(f"Logs error: {logs_error}")
    print_info(f"Environment setup: {envs}")
    print_info(f"Modules to load: {modules}")

    jobs = Jobs()
    jobs.generate_job_based_on_params(
        name="GeneratedJob",
        account="default",
        exec_command=[command],
        cores=cores,
        gpu=gpu,
        mode=qos,
        nodes=nodes,
        time=time,
        ntasks=ntasks,
        partition=partition,
        environment_commands=envs,
        module_names=modules,
        logs_default=logs_default,
        logs_error=logs_error,
    )
    # Generate the SLURM script
    reports: list[SlurmifyValidationReport] = start_validation(jobs.get_jobs())

    if len(reports) > 0:
        report: SlurmifyValidationReport = reports[0]

        if not report.valid:
            print_error("Slurm script is not valid")
            print_error(report.error_report)
            return

    job = jobs.get_jobs()[0]
    slurm = generate_slurm_script(job, create_file=True)
    pass


def main() -> None:
    # Add performance metrics time
    start_time = time.time()
    # Parse command line arguments
    args = arg_handler()

    if args.verbose:
        enable_printing()
        print_info("Verbose mode enabled")

    if args.skip_module_check:
        # global skip_modules
        # skip_modules = True
        set_skip_modules(True)

    # Check if the user wants to generate a new configuration file
    if args.init:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(
            current_dir, "Templates", "SingleSystemTemplate.py"
        )
        new_file_path = args.init

        # check if py was specified if not add it
        if not new_file_path.endswith(".py"):
            new_file_path += ".py"

        print_info(f"Generating new configuration file: {new_file_path}")
        with open(template_path, "r") as template_file:
            template_content = template_file.read()
        with open(new_file_path, "w") as new_file:
            new_file.write(template_content)
        print_success(f"New configuration file generated: {new_file_path}")

        end_time = time.time()
        elapsed_time = end_time - start_time

        print_info(f"Elapsed time: {elapsed_time:.2f} seconds", debug=True)
        return

    if args.command:
        print_info("Generating SLURM script")
        generate_slurm_script_from_args(args)
        end_time = time.time()
        elapsed_time = end_time - start_time
        return

    if args.test:

        testing_configs("TestConfigs/", auto_run_slurm=True)
        end_time = time.time()
        elapsed_time = end_time - start_time

        print_info(f"Elapsed time: {elapsed_time:.2f} seconds", debug=True)
        return

    if args.file:
        valid, error_reports = validate_slurmify_config(args.file)

        if not valid:
            print_error("SLURM configuration file is not valid")
            for report in error_reports:
                print(report)
            return

        validation_only = args.validation_only

        for report in error_reports:
            if not validation_only:
                if report.valid:
                    print_success(f"Job {report.job_name} is valid")

                    out = "./out"
                    if args.output:
                        out = args.output

                    # Generate the SLURM script
                    slurm = generate_slurm_script(
                        report.job, create_file=True, output_path=out
                    )
                    print_success(f"SLURM script generated: {slurm}")

            print(report)

        end_time = time.time()
        elapsed_time = end_time - start_time

        print_info(f"Elapsed time: {elapsed_time:.2f} seconds", debug=True)
        return

    if args.web:
        print_info("Web mode enabled")

        streamlit_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "streamlit_main.py"
        )
        # Launch streamlit as a subprocess
        subprocess.run(["streamlit", "run", streamlit_path])
        return

    if args.api:
        print_info("API mode enabled")

        api_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "main_api.py"
        )

        # Launch api as a subprocess
        subprocess.run(["python", api_path])
        return

    if args.module_search:
        modules = search_module(
            args.module_search,
        )
        print("Module search completed")
        print("Found modules:")
        for module in modules:
            versions = ", ".join(str(v) for v in modules[module])
            print(f"{module:<30} {versions}")
        end_time = time.time()
        elapsed_time = end_time - start_time


if __name__ == "__main__":
    main()
