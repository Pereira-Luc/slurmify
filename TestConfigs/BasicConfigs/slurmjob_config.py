from utils.config_info import (
    Resources,
    System,
    Job,
    Jobs,
    Environment,
    Module,
    Modules,
    Logs,
)

# Create Jobs container
jobs = Jobs()

# Define resources
resources = Resources(
    account="lxp",
    partitions="cdpu",
    cores=20,
    gpu=1,
    mode="default",
    nodes=1,
    time="00:15:00",
    ntasks=1,
)

# Create system configuration
system = System(resources=resources)

# Command to execute
exec_command = ["srun python main.py"]

# No log configuration specified
logs = None

# No environment configuration specified
environments = None

# Configure modules
modules_list = [Module(name=module_name) for module_name in ["Test/test1"]]
modules = Modules(list_of_modules=modules_list)

# Create the job
job = Job(
    name="SlurmJob",
    system=system,
    exec_command=exec_command,
    environments=environments,
    logs=logs,
    modules=modules,
)

# Add job to the Jobs collection
jobs.add_job(job)

# This variable needs to be present for Slurmify to find the jobs
Jobs = jobs
