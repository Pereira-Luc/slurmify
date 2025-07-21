from utils.config_info import (
    Job,
    Environment,
    System,
    Jobs,
    Resources,
    Logs,
    Modules,
    Module,
)

# Create a Resources object with 5 nodes, each having 20 cores and 2 GPUs
resources = Resources(
    account="your_account_name",  # Replace with your actual account name
    partitions="gpu",
    cores=20,
    gpu=2,
    mode="exclusive",
    nodes=5,
    time="48:00:00",  # Adjust the time as needed
)

# Create a Job object for LLM training
job = Job(
    name="llm-training-job",
    system=System(resources),
    exec_command="python train_llm.py",  # Replace with your actual command
    environments=[Environment("conda_env", ["source activate myenv"])],
    logs=Logs(default="logs/output.log", error="logs/error.log"),
    modules=Modules([Module("pytorch"), Module("cuda")]),  # Add necessary modules
)

# Create a Jobs object and add the job
jobs = Jobs()
jobs.add_job(job)
