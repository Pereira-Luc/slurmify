from utils.config_info import Job, System, Jobs, Resources

# Initialize Resources with cores and gpus as defined in the suggestion
resources = Resources(
    account="lxp",
    cores=4,
    gpu=None,
    mode="default",
    nodes=1,
    time="00:15:00",
    partitions="cpu",
    ntasks=1,
)

system = System(resources=resources)
job = Job(name="main_job", system=system, exec_command="python main.py")

# Initialize the Jobs object with correct variable name
Jobs = Jobs()

# Add the job to the Jobs object
Jobs.add_job(job)
