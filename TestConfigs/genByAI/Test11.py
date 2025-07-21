from utils.config_info import (
    Job,
    Environment,
    System,
    Jobs,
    Resources,
    Logs,
)

# Define log locations
logs = Logs(default="job-%j.out", error="job-%j.err")

resources = Resources(
    account="lxp",  # replace 'your_account' with a valid Slurm account if required
    cores=20,
    gpu=3,
    mode="default",
)

system_config = System(resources=resources)

# Create job
my_job = Job(
    name="PythonJob",
    environments=[],  # You can add environment configurations here if needed
    system=system_config,  # Pass the system configuration instance containing resource settings
    logs=logs,
    exec_command="srun python main.py",  # replace 'main.py' with your real script name
)
