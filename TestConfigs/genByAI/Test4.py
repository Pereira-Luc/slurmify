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

# Define the environments needed for the job
python_env = Environment(
    name="PythonEnv",
    commands=["pip install -r requirements.txt", "python setup.py install"],
)

# Define the modules to be loaded (if any)
modules = Modules(list_of_modules=[Module(name="module0"), Module(name="module1")])

# Define the resources for the job
resources = Resources(
    cores=128,
    gpu=1,
    mode="gpu",  # Corrected to a valid Slurm partition name
    nodes=5,  # Set to a reasonable number of nodes
    account="lxp",
    ntasks=1,
    time="00:10",  # Adjust the time as needed for your job
)

# Define the system configuration for the job
system = System(name="Program", resources=resources)

# Define the logs for the job
logs = Logs(default="logs_Path", error="error_logs_Path")

# Define the execution command for the job
exec_command = "srun python my_script.py"

# Create a Jobs collection and add our main job
Jobs = Jobs()
Jobs.add_job(
    Job(
        name="MainJob",
        system=system,
        environments=[python_env],
        logs=logs,
        modules=modules,
        exec_command=exec_command,
    )
)

# Now, you can use the `Jobs` object to generate and submit your Slurm job scripts.
