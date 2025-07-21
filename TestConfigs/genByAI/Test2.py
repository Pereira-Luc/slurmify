from utils.config_info import (
    Job,
    System,
    Jobs,
    Resources,
    Environment,
    Logs,
    Modules,
    Module,
)

# Define the resources for the job
resources = Resources(
    cores=128,
    gpu=1,
    mode="default",
    nodes=1,
    account="lxp",
    ntasks=2,
    time="00:10",
    partitions="gpu",
)

# Define the system configuration
system = System(name="Program", resources=resources)

# Define the environment setup commands
environment = Environment(
    name="PyEnv",
    commands=["pip install -r requirements.txt", "python setup.py install"],
)

# Define the log paths
logs = Logs(default="logs_Path", error="error_logs_Path")

# Define the modules to be loaded
modules = Modules(list_of_modules=[Module(name="module0"), Module(name="module1")])

# Define the execution command
exec_command = "srun python my_script.py"

# Create a Slurm job
job = Job(
    name="MainJob",
    system=system,
    environments=[environment],
    logs=logs,
    modules=modules,
    exec_command=exec_command,
)

# Add the job to a Jobs collection
jobs = Jobs()
jobs.add_job(job)
