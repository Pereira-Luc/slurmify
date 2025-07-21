from utils.config_info import Jobs, System, Job, Resources, Environment

# Define the System object with appropriate resources.
system = System(name="Program", resources=Resources(account="lxp", cores=20, gpu=1))

# Create a new job configuration.
job_config = Job(
    name="main_job",
    system=system.resources,
    environments=[Environment(name="run_script_env", commands=["python ./main.py"])],
    exec_command="python main.py",
)

# Initialize the Jobs object and add your job to it.
Jobs = Jobs()  # Corrected variable name
Jobs.add_job(job_config)  # Calling method on instance with correct variable name
