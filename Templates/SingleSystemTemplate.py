"""
Slurmify Configuration Template

This template provides a comprehensive example of how to create a Slurmify configuration.
Replace the placeholder values with your specific requirements.
"""

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

#############################################
# Define environment setup commands (optional)
#############################################
# Environment objects define shell commands to set up your job environment
my_environment = Environment(
    name="MyEnvironment",  # A name for this environment setup
    commands=[
        # List of shell commands to run at job startup
        "export PATH=/custom/path:$PATH",
        "export MY_VAR=my_value",
        # Add any environment variables, paths, or setup commands needed
        "conda activate my_env",  # Example for conda environment
        "pip install -r requirements.txt",  # Example for pip installations
    ],
)

#############################################
# Define computational resources (required)
#############################################
my_resources = Resources(
    # Required parameter:
    account="your_project_account",  # Your project account ID (e.g., "lxp")
    # Optional parameters with defaults:
    partitions="cpu",  # Partition to use: "cpu", "gpu", "fpga", or "largemem"
    cores=1,  # CPUs per task (e.g., 16, 32, 128)
    gpu=None,  # GPUs per task (None or integer like 1, 2, 4)
    mode="default",  # QoS mode: "dev", "test", "short", "short-preempt", "default", "long", "large", "urgent"
    nodes=1,  # Number of nodes to request
    time="00:15:00",  # Maximum job runtime in format "HH:MM:SS" (e.g., "01:00:00" for 1 hour)
    ntasks=1,  # Number of tasks
)

#############################################
# Define system configuration (required)
#############################################
my_system = System(
    name="MySystem",  # Optional name for your system
    resources=my_resources,  # Resources object defined above (required)
)

#############################################
# Define log file paths (optional)
#############################################
my_logs = Logs(
    default="job-%j.out",  # Path for stdout logs (%j will be replaced with job ID)
    error="job-%j.err",  # Path for stderr logs (%j will be replaced with job ID)
)

#############################################
# Define modules to load (optional)
#############################################
my_modules = Modules(
    list_of_modules=[
        Module(name="env/release/2023.1"),  # Example module name
        Module(name="Python/3.10.8-GCCcore-12.2.0"),  # Example module name
        Module(name="CUDA/11.8.0"),  # Example for GPU jobs
        # Add any modules your job needs to load
    ]
)

#############################################
# Create job definition (required)
#############################################
my_job = Job(
    name="MyJob",  # Job name (required)
    system=my_system,  # System object defined above (required)
    exec_command="srun python my_script.py",  # Command to execute (required)
    # Optional parameters:
    environments=[my_environment],  # List of Environment objects or None
    logs=my_logs,  # Logs object or None
    modules=my_modules,  # Modules object or None
)

#############################################
# Create Jobs collection and add job (required)
#############################################
# IMPORTANT: The variable MUST be named "Jobs" (case-sensitive)
Jobs = Jobs()  # Create Jobs collection
Jobs.add_job(my_job)  # Add your job(s) to the collection

# For multiple jobs, you can add more:
# Jobs.add_job(my_second_job)
