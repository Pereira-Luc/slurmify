from utils.config_info import Resources, System, Job, Jobs, Environment, Module, Modules, Logs

# Create Jobs container
jobs = Jobs()

# Define resources
resources = Resources(
    account="lxp",
    partitions="cpu",
    cores=12,
    gpu=None,
    mode="dev",
    nodes=1,
    time="00:15:00",
    ntasks=1
)

# Create system configuration
system = System(resources=resources)

# Command to execute
exec_command = ['srun python\tmain.py']

# No log configuration specified
logs = None

# No environment configuration specified
environments = None

# Configure modules
modules_list = [Module(name=module_name) for module_name in ['Cuda/10']]
modules = Modules(list_of_modules=modules_list)

# Create the job
job = Job(
    name="MyJob",
    system=system,
    exec_command=exec_command,
    environments=environments,
    logs=logs,
    modules=modules
)

# Add job to the Jobs collection
jobs.add_job(job)

# This variable needs to be present for Slurmify to find the jobs
Jobs = jobs
