from utils.config_info import Job, System, Jobs, Resources

Jobs = Jobs()

Jobs.add_job(
    Job(
        name="InvalidTimeJob",
        system=System(
            name="BadTimeSystem",
            resources=Resources(
                account="lxp",
                cores=4,
                gpu=None,
                mode="default",
                nodes=1,
                time="24h",  # Error: Invalid time format
                partitions="cpu",
                ntasks=1,
            ),
        ),
        exec_command="srun sleep 30",
    )
)
