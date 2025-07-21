from utils.config_info import Job, Resources

# Define the system resources
resources = Resources(
    account="lxp",
    nodes=1,
    ntasks_per_node=4,
    cpus_per_task=1,
    time="00:30:00",  # 30 minutes runtime
    partition="gpu",
    gpus_per_node=1,
)

# Define the environment setup commands
environment_setup = [
    "module purge",
    "module load python/3.8",
    "pip install -r requirements.txt",
]

# Define the main execution command
execution_command = "srun python my_script.py"

# Create a new Slurm job instance
job = Job(
    name="AIJob",
    resources=resources,
    output="ai_job_output.log",
    error="ai_job_error.log",
    script_commands=[*environment_setup, execution_command],
)

# Submit the job to the Slurm scheduler
job.submit()
