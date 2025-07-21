from utils.config_info import Job, Environment, Resources, Jobs, System

# Define the Python environment setup
python_env = Environment(
    name="PyEnv", commands=["pip install -r requirements.txt", "python main.py"]
)

resources = Resources(account="lxp", cores=50, gpu=2, mode="default")

# Define a System instance with resources
system_with_resources = System(
    name="Program", resources=resources  # Assigning the 'resources' object correctly.
)

job = Job(
    name="MyJob",  # Name of your job
    environments=[python_env],  # List of environment objects
    system=system_with_resources,  # Correctly assigning a System instance
    logs=None,
    modules=None,
    exec_command="srun python my_script.py",  # Execution command for the job.
)

# Create a Jobs object and add your Job to it
Jobs = Jobs()  # Renamed from jobs_collection to simply "Jobs"
Jobs.add_job(job)  # Adding the defined job
