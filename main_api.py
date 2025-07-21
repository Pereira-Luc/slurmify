from fastapi import FastAPI
import sys
import os
import tempfile
import logging
import uvicorn


from api.apiConfig import (
    ConfigRequest,
    ValidationResponse,
    ValidationResult,
    ParameterRequest,
)
from utils.slurmifyLoader import load_python_conf_file
from utils.slurmifyValidationReport import SlurmifyValidationReport
from utils.moduleListHandler import get_module_list

# Add parent directory to path to import from project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import project modules
from utils.config_info import Job, Jobs
from utils.func import (
    generate_slurm_script,
    get_slurmify_jobs,
    start_validation,
)

app = FastAPI(
    title="SLURMify Validation API",
    description="API for validating SLURM configurations",
)


def create_tmp_file():
    pass


def create_log_api(
    tmp_name,
    extension,
    content,
    report_name=None,
    path="api/logs",
):
    print(f"Tmp_name: {tmp_name}")
    print(f"Creating log file: {tmp_name}.{extension}")
    print(f"Content: {content}")
    print(f"Path: {path}")

    try:
        path_to_save = f"{path}/{tmp_name}"

        os.makedirs(f"{path_to_save}", exist_ok=True)

        if report_name:
            file_path = f"{path_to_save}/{report_name}.{extension}"
        else:
            file_path = f"{path_to_save}/{tmp_name}.{extension}"

        with open(f"{ file_path }", "w") as f:
            f.write(content)
    except Exception as e:
        logger.error(f"Failed to save temporary file: {str(e)}")


# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add parent directory to path to import from project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@app.post("/validate", response_model=ValidationResponse)
async def validate_config(request: ConfigRequest):
    """Validate a SLURM configuration"""
    logger.debug("Starting validation request")
    logger.debug(f"Received code of length: {len(request.code)}")

    logger.debug(f"Request code: {request.code}")

    # Create a file to store the code
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as temp_file:
        temp_file.write(request.code)
        temp_file_path = temp_file.name
        temp_file_name = os.path.basename(temp_file_path).replace(".py", "")

    logger.debug(f"Temp file created: {temp_file_path}")
    logger.debug(f"Temp file name: {temp_file_name}")

    create_log_api(
        tmp_name=temp_file_name, extension="py", content=request.code, path="api/logs"
    )

    response = ValidationResponse(valid=True, results=[])

    try:
        config_path = "systemConfig/conf.yaml"
        path_of_python_file = temp_file_path

        module, error_report = load_python_conf_file(path_of_python_file)
        jobs: list[Job] = get_slurmify_jobs(module, error_report)

        if not jobs:
            print(error_report)
            response.valid = False

            response.results.append(
                ValidationResult(
                    job_name=error_report.job_name,
                    valid=False,
                    result=error_report.for_llm_json_safe(),
                )
            )

            create_log_api(
                tmp_name=temp_file_name,
                report_name=error_report.job_name,
                extension="md",
                content=error_report.for_llm_json_safe(),
                path="api/logs",
            )

            return response

        list_of_reports = start_validation(jobs)

        if not list_of_reports:
            response.valid = True
            response.results.append(
                ValidationResult(
                    job_name="Job Is Valid",
                    valid=True,
                    result="No validation reports generated.",
                )
            )
            return response

        for list_of_report in list_of_reports:
            if not list_of_report.valid:
                response.valid = False
                response.results.append(
                    ValidationResult(
                        job_name=list_of_report.job_name,
                        valid=False,
                        result=list_of_report.for_llm_json_safe(),
                    )
                )
            else:
                response.results.append(
                    ValidationResult(
                        job_name=list_of_report.job_name,
                        valid=True,
                        result=list_of_report.for_llm_json_safe(),
                    )
                )

        create_log_api(
            tmp_name=temp_file_name,
            report_name="validation_report",
            extension="md",
            content=response.results[0].result,
            path="api/logs",
        )

    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                logger.debug(f"Removed temporary file: {temp_file_path}")
            except Exception as e:
                logger.error(f"Failed to remove temporary file: {str(e)}")

    logger.debug(response.results)

    return response


@app.post("/GenerateConfigParameters", response_model=ValidationResponse)
async def generate_config_parameters(request: ParameterRequest):
    try:
        print(f"Request: {request}")
        print(f"Request exec_command: {request.exec_command}")

        return ValidationResponse(
            valid=True,
            results=[
                ValidationResult(
                    job_name=request.name,
                    valid=True,
                    result=f"Configuration parameters generated for job: {request.name}",
                )
            ],
        )

    except Exception as e:
        logger.error(f"Error in generate_config_parameters: {str(e)}")
        return {"error": "Failed to generate configuration parameters"}


@app.get("/GenerateConfigParameters", response_model=ValidationResponse)
async def generate_config_parameters(
    name: str,
    account: str,
    exec_command: str,
    cores: int = 1,
    gpu: int | None = None,
    mode: str = "default",
    nodes: int | None = None,
    time: str = "00:15:00",
    ntasks: int = 1,
    partition: str = "cpu",
    environment_commands: str | None = None,
    module_names: str | None = None,
    logs_default: str | None = None,
    logs_error: str | None = None,
):
    try:
        print(
            f"Request parameters - name: {name}, account: {account}, exec_command: {exec_command}, partition: {partition}, time: {time}, logs_default: {logs_default}, logs_error: {logs_error}"
        )
        print(
            f"Other parameters - cores: {cores}, gpu: {gpu}, mode: {mode}, nodes: {nodes}, ntasks: {ntasks}"
        )

        print(f"Module names: {module_names}")

        jobs_instance = Jobs()
        jobs_instance.clear_jobs()

        jobs_instance.generate_job_based_on_params(
            name=name,
            account=account,
            exec_command=[exec_command],
            cores=cores,
            gpu=gpu,
            mode=mode,
            nodes=nodes,
            time=time,
            ntasks=ntasks,
            partition=partition,
            environment_commands=(
                environment_commands.split(",") if environment_commands else None
            ),
            module_names=module_names.split(",") if module_names else None,
            logs_default=logs_default,
            logs_error=logs_error,
        )

        reports: list[SlurmifyValidationReport] = start_validation(
            jobs_instance.get_jobs()
        )

        if len(reports) > 0:
            report: SlurmifyValidationReport = reports[
                0
            ]  # there will always only be one for now

            print(report)

            if not report.valid:
                logger.error(f"Validation failed: {report.for_llm_json_safe()}")
                return ValidationResponse(
                    valid=False,
                    results=[
                        ValidationResult(
                            job_name=report.job_name,
                            valid=False,
                            result=report.for_llm_json_safe(),
                        )
                    ],
                )

        job = report.job
        if not job:
            logger.error("No job found in the validation report")
            return ValidationResponse(
                valid=False,
                results=[
                    ValidationResult(
                        job_name="Error",
                        valid=False,
                        result="No job found in the validation report",
                    )
                ],
            )

        slurm = generate_slurm_script(job, create_file=False)

        return ValidationResponse(
            valid=True,
            results=[
                ValidationResult(
                    job_name=name,
                    valid=True,
                    result=f"{slurm}",
                    report=report.for_llm_json_safe(),
                )
            ],
        )

    except Exception as e:
        logger.error(f"Error in generate_config_parameters: {str(e)}")
        return ValidationResponse(
            valid=False,
            results=[
                ValidationResult(
                    job_name="Error",
                    valid=False,
                    result=f"Failed to generate parameters: {str(e)}",
                )
            ],
        )


@app.get("/template")
async def get_template():
    """Get a template for SLURM configuration"""
    try:
        with open("Templates/SingleSystemTemplate.py", "r") as template_file:
            template_content = template_file.read()
        return {"template": template_content}
    except Exception as e:
        logger.error(f"Error reading template file: {str(e)}")
        return {"error": "Failed to read template file"}


@app.get("/module_search")
async def get_modules_and_versions(search: str):
    """Search for modules and their versions"""

    try:
        module_list = get_module_list()
        search_results = module_list.search_modules_with_versions(search)
        return {"modules": search_results}
    except Exception as e:
        logger.error(f"Error searching modules: {str(e)}")
        return {"error": "Failed to search modules"}


# API call to test if the API is running
@app.get("/testAPI")
async def test_api():
    return {"message": "API is running"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
