from utils.config_info import Job, Jobs, Resources

# Create a job - intentionally with structural problems
job = Job(
    name="gpu_job",
    exec_command="python script.py",
    resources=Resources(  # Problem: Job expects 'system', not 'resources'
        account="lxp",
        gpu=1,
        nodes=1,
        cores=4,
        mode="default",
        # Problem: Missing required parameters: partitions, time, ntasks
    ),
)

# Problem: Variable should be named 'Jobs' not 'jobs' (case sensitive)
jobs = Jobs()
jobs.add_job(job)
