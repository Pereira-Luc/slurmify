from utils.config_info import Job, System, Jobs, Resources

# Create a Jobs collection
Jobs = Jobs()

# Add a job with 5 nodes each with 20 cores
Jobs.add_job(
    Job(
        name="PythonScriptJob",
        system=System(
            name="lxp",
            resources=Resources(
                account="your_project_account",
                nodes=5,
                cores=20,
                time="01:00:00",  # 1 hour runtime [source_id>0</source_id]
            ),
        ),
        exec_command="srun python my_script.py",  # Command to execute
    )
)
