from utils.config_info import (
    Job,
    System,
    Resources,
    Logs,
    Modules,
    Module,
    Jobs,  # Added this line
)

my_resources = Resources(
    account="lxp",  # Your project account ID (e.g., 'lxp')
    cores=64,
    gpu=2,
    mode="default",
    time="00:15:00",
)

my_system = System(
    resources=my_resources,  # Resources object defined above (required)
)

my_logs = Logs(
    default="job-%j.out",  # Path for stdout logs (%j will be replaced with job id)
    error="job-%j.err",  # Path for stderr logs (%j will be replaced with job id)
)

my_modules = Modules(list_of_modules=[Module(name="CUDA/11.0")])

# Create job definition (required)
my_job = Job(
    name="MyJob",  # Job name (required)
    system=my_system,  # System object defined above (required)
    exec_command="srun python my_script.py",  # Command to execute (required)
    logs=my_logs,
    modules=my_modules,
)

# Create Jobs collection and add job (required)
Jobs = Jobs()  # Corrected variable name as required by the validation rule
Jobs.add_job(my_job)
