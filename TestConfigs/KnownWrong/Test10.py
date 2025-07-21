from utils.config_info import Job, System, Jobs, Resources

Jobs = Jobs()

Jobs.add_job(
    Job(
        name="MissingAccountJob",
        system=System(
            name="NoAccountSystem",
            resources=Resources(
                account=None,  # Error: Missing account
                cores=4,
                gpu=None,
                mode="default",
                nodes=1,
                time="00:15:00",
                partitions="cpu",
                ntasks=1,
            ),
        ),
        exec_command="srun sleep 30",
    )
)
