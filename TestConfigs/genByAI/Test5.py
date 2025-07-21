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

# Define resources
resources = Resources(
    cores=64,
    gpu=4,
    mode="def",  # default partition mode
    nodes=1,
    account="lxp",
    ntasks=1,  # corrected from ntasks_per_node to just ntasks
    time="02:00:00",  # job runtime of 2 hours
    partitions="gpu",  # specify the partition if needed
)

# Define system
system = System(
    name="AI-Cluster",
    resources=resources,
)

# Define environment setup commands
environment_setup_commands = [
    "module load python/3.8",  # Load Python module
    "pip install -r requirements.txt",  # Install dependencies
    "python setup.py install",  # Install any custom packages
]

# Create environment object
environment = Environment(name="AI-Environment", commands=environment_setup_commands)

# Define logging paths
logs = Logs(default="job-%j.out", error="job-%j.err")

# Define modules (if applicable)
modules = Modules(list_of_modules=[Module(name="module0"), Module(name="module1")])

# Define execution command
exec_command = "srun python your_ai_script.py"  # Replace with your AI script

# Create a Job object
job = Job(
    name="AI-Training-Job",
    environments=[environment],
    system=system,
    logs=logs,
    modules=modules,
    exec_command=exec_command,
)

# Create Jobs collection and add the job
Jobs = Jobs()
Jobs.add_job(job)
