from utils.config_info import (
    Job,
    Environment,
    System,
    Resources,
    Jobs,  # Correctly importing the Jobs class
)

# Define resources with correct attributes
resources = Resources(
    account="lxp",  # Replace 'your_account_name' with an actual Slurmify account name
    cores=20,  # Corrected from cpus_per_task
    gpu=4,  # Ensure you use 'gpu' instead of 'gpus'
)

# Define the job with corrected exec_command as a string
job = Job(
    name="main_job",
    system=System(resources),
    exec_command="python3 main.py",  # This is now correctly set as a string
)

# Instantiate and add your job to the Jobs collection using the required variable name "Jobs"
Jobs = Jobs()  # Corrected instance name to avoid confusion with class name
Jobs.add_job(job)  # Adding your defined job into the collection
