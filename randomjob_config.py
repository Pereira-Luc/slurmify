from utils.config_info import Resources, System, Job, Jobs, Environment, Module, Modules, Logs

# Create Jobs container
jobs = Jobs()

# Define resources
resources = Resources(
    account="lxp",
    partitions="gpu",
    cores=200,
    gpu=200,
    mode="default",
    nodes=1,
    time="1",
    ntasks=1
)

# Create system configuration
system = System(resources=resources)

# Command to execute
exec_command = ['exec']

# No log configuration specified
logs = None

# No environment configuration specified
environments = None

# No modules specified
modules = None

# Create the job
job = Job(
    name="RandomJob",
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
