import json
import requests
import streamlit as st
from utils.config_info import Job, Jobs
from utils.func import generate_slurm_script, start_validation
from utils.slurmifyValidationReport import SlurmifyValidationReport


def get_layout():
    left_layout, right_layout = st.columns(2)
    return left_layout, right_layout


def get_modules_list():
    selected_modules = st.session_state.selected_modules
    modules = []

    for selected_module in selected_modules:
        module_versions = st.session_state.get(f"version_{selected_module}")
        if module_versions is not None:
            modules.append(f"{selected_module}/{module_versions}")

    return modules


def text_area_to_list(text_area: str) -> list[str]:
    """
    Convert a text area string to a list of strings.

    Args:
        text_area (str): The text area string.

    Returns:
        list[str]: The list of strings.
    """
    if text_area is None or text_area == "":
        return []
    return [line.strip() for line in text_area.split("\n") if line.strip() != ""]


def get_slurm(layout):
    jobs_instance = Jobs()
    jobs_instance.clear_jobs()
    if st.session_state.subsched:
        exec_command = text_area_to_list(st.session_state.subsched_commands)
    else:
        exec_command = text_area_to_list(st.session_state.exec_command)

    jobs_instance.generate_job_based_on_params(
        name=st.session_state.job_name,
        account=st.session_state.selected_account,
        exec_command=exec_command,
        cores=st.session_state.selected_cpus,
        partition=st.session_state.selected_partion,
        nodes=st.session_state.selected_nodes,
        ntasks=st.session_state.selected_ntasks,
        mode=st.session_state.selected_qos,
        logs_default=st.session_state.selected_logs_default,
        logs_error=st.session_state.selected_logs_error,
        environment_commands=text_area_to_list(st.session_state.environment_commands),
        module_names=get_modules_list(),
        gpu=st.session_state.selected_gpus,
    )

    reports: list[SlurmifyValidationReport] = start_validation(jobs_instance.get_jobs())

    if len(reports) > 0:
        report: SlurmifyValidationReport = reports[
            0
        ]  # there will always only be one for now

        if not report.valid:
            layout.error("Job is not valid")
            layout.write(report.for_llm())

    for job_instance in jobs_instance.get_jobs():
        print(job_instance.name)

    # Job is valid
    job = jobs_instance.get_jobs()[0]

    slurm = generate_slurm_script(job, create_file=False)
    return slurm, job


def init_states():
    # Initialize states
    if "job_name" not in st.session_state:
        st.session_state.job_name = "main_job"
    if "selected_partion" not in st.session_state:
        print("Initializing selected_partion")
        st.session_state.selected_partion = "cpu"
    if "selected_account" not in st.session_state:
        print("Initializing selected_account")
        st.session_state.selected_account = "lxp"
    if "selected_JWT_token" not in st.session_state:
        print("Initializing selected_JWT_token")
        st.session_state.selected_JWT_token = None
    if "selected_gpus" not in st.session_state:
        print("Initializing selected_gpus")
        st.session_state.selected_gpus = 0
    if "selected_cpus" not in st.session_state:
        print("Initializing selected_cpus")
        st.session_state.selected_cpus = 1
    if "exec_command" not in st.session_state:
        st.session_state.exec_command = "wait 30"
    if "selected_qos" not in st.session_state:
        st.session_state.selected_qos = "default"
    if "selected_ntasks" not in st.session_state:
        st.session_state.selected_ntasks = 1
    if "selected_nodes" not in st.session_state:
        st.session_state.selected_nodes = 1
    if "selected_time" not in st.session_state:
        st.session_state.selected_time = "00:15:00"
    if "selected_logs_default" not in st.session_state:
        st.session_state.selected_logs_default = f"{st.session_state.job_name}-%j.out"
    if "selected_logs_error" not in st.session_state:
        st.session_state.selected_logs_error = f"{st.session_state.job_name}-%j.err"
    if "environment_commands" not in st.session_state:
        st.session_state.environment_commands = None
    if "module_names" not in st.session_state:
        st.session_state.module_names = None
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "selected_workdir" not in st.session_state:
        st.session_state.selected_workdir = ""
    if "selected_modules" not in st.session_state:
        st.session_state.selected_modules = []
    if "job_id" not in st.session_state:
        st.session_state.job_id = None
    if "job_data" not in st.session_state:
        st.session_state.job_data = None
    if "subsched" not in st.session_state:
        st.session_state.subsched = False
    if "subsched_commands" not in st.session_state:
        st.session_state.subsched_commands = None


def get_node_info(jwt_token: str, node_id: str):
    """
    Get node information from the Slurm server.

    Args:
        jwt_token (str): The JWT token for authentication.
        node_id (str): The node ID to retrieve information for.

    Returns:
        dict: The node information.
    """
    SLURM_URL = "https://slurm.cloud.lxp.lu"
    API_VER = "v0.0.40"
    SLURM_JWT = jwt_token

    response = requests.get(
        f"{SLURM_URL}/slurm/{API_VER}/node/{node_id}",
        headers={
            "X-SLURM-USER-TOKEN": f"{SLURM_JWT}",
        },
    )

    response.raise_for_status()
    print(json.dumps(response.json(), indent=2))

    if response.status_code != 200:
        # Save the information in the session state
        st.session_state.node_info = None
        return None
    else:
        # Save the information in the session state
        st.session_state.node_info = response.json()
        return response.json()


def submit_slurm_job(jwt_token: str, job: Job, slurm: str = None, layout=None):
    """
    Submit the Slurm job to the cluster.

    Documentation: https://docs.lxp.lu/web_services/slurmrestd/#__tabbed_5_2

    Args:
        jwt_token (str): The JWT token for authentication.
        account (str): The account to use for the job.
        user_name (str): The user name for the job.

    """
    print("Submitting job...")
    if jwt_token is None:
        layout.error("JWT token is required to submit the job.")
        return
    if job is None:
        layout.error("Job is required to submit the job.")
        return

    SLURM_URL = "https://slurm.cloud.lxp.lu"
    API_VER = "v0.0.40"
    SLURM_JWT = jwt_token
    USER_NAME = st.session_state.username
    ACCOUNT = job.system.resources.account

    # print(slurm)
    print(st.session_state.selected_workdir)
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
                "current_working_directory": f"{st.session_state.workdir}",
                "environment": [f"USER={USER_NAME}"],
            },
        },
    )

    response.raise_for_status()
    print(json.dumps(response.json(), indent=2))

    if response.json().get("job_id") is None:
        layout.error("Job submission failed.")
        return

    job_id = response.json().get("job_id")
    layout.success("Job submitted successfully! Job ID: " + str(job_id))
    st.session_state.job_id = job_id


def ping_slurm(jwt_token: str, user_name: str = "lcpereira"):
    """
    Ping the Slurm server to check if it is reachable.

    Args:
        None

    Returns:
        bool: True if the server is reachable, False otherwise.
    """
    left_layout, right_layout = get_layout()

    if jwt_token is None:
        print("JWT token is required to ping the server.")
        right_layout.error("JWT token is required to ping the server.")
        return

    SLURM_URL = "https://slurm.cloud.lxp.lu"
    API_VER = "v0.0.40"
    SLURM_JWT = jwt_token
    USER_NAME = user_name

    response = requests.get(
        f"{SLURM_URL}/slurm/{API_VER}/ping",
        headers={
            "X-SLURM-USER-NAME": f"{USER_NAME}",
            "X-SLURM-USER-TOKEN": f"{SLURM_JWT}",
        },
    )

    response.raise_for_status()
    print(json.dumps(response.json(), indent=2))

    right_layout.write(response.json())


def print_all_states():
    """Print all states in the session state."""
    print("Session State:")
    print("--------------")
    for key, value in st.session_state.items():
        print(f"{key}: {value}")
    print("--------------")


def get_job_information(job_id, jwt_token):
    """
    Get job information from the Slurm server.

    Args:
        job_id (str): The job ID to retrieve information for.
        jwt_token (str): The JWT token for authentication.

    Returns:
        dict: The job information.
    """
    SLURM_URL = "https://slurm.cloud.lxp.lu"
    API_VER = "v0.0.40"
    SLURM_JWT = jwt_token

    response = requests.get(
        f"{SLURM_URL}/slurm/{API_VER}/job/{job_id}",
        headers={
            "X-SLURM-USER-TOKEN": f"{SLURM_JWT}",
        },
    )

    # print(json.dumps(response.json(), indent=2))

    response.raise_for_status()

    if response.status_code != 200:
        # Save the information in the session state
        st.session_state.job_data = None
        st.session_state.job_id = None
        st.session_state.job_status = None
    else:
        # Save the information in the session state
        st.session_state.job_data = response.json()
        st.session_state.job_id = job_id
        st.session_state.job_status = response.json().get("job_state")

    # return response.json()


def cancel_job(jwt_token: str, job_id: str):
    """
    Cancel a job on the Slurm server.

    Args:
        jwt_token (str): The JWT token for authentication.
        job_id (str): The job ID to cancel.

    Returns:
        bool: True if the job was canceled successfully, False otherwise.
    """
    SLURM_URL = "https://slurm.cloud.lxp.lu"
    API_VER = "v0.0.40"
    SLURM_JWT = jwt_token

    response = requests.delete(
        f"{SLURM_URL}/slurm/{API_VER}/job/{job_id}",
        headers={
            "X-SLURM-USER-TOKEN": f"{SLURM_JWT}",
        },
    )

    response.raise_for_status()

    if response.status_code == 200:
        return True
    else:
        return False
