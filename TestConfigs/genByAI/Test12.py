from utils.config_info import (
    Job,
    System,
    Resources,
    Jobs,
    Environment,
)  # Importing the necessary classes including Environment class for environments

gpus_per_node = 4
account_name = "lxp"  # Replace with actual account name

# Define resources for the job using valid parameters including 'account'
resources = Resources(cores=64, gpu=gpus_per_node, account=account_name)

# Setup system with defined resources and name it accordingly
system_config = System(resources, name="main_job_resource_reqs")

# Create a list of Environment objects (You can customize these environments as needed)
env_list = [Environment(name="PythonEnv", commands=["source /path/to/python_env"])]

# Describe the job to be executed by Slurmify
job_to_run = Job(
    name="run_main",
    system=system_config,
    exec_command="python3 main.py",
    environments=env_list,  # Add the list of Environment objects here
)

# Create a Jobs object with correct instance name and add defined job to it.
Jobs = Jobs()  # Changed from j_collection to Jobs
Jobs.add_job(job_to_run)
