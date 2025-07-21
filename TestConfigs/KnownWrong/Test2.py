from utils.config_info import Job, System, Jobs, Resources

Jobs = Jobs()

Jobs.add_job(
    Job(
        name="InvalidModeJob",
        system=System(
            name="BadModeSystem",
            resources=Resources(
                account="lxp",
                cores=4,
                gpu=None,
                mode="unlimited",  # Error: This mode doesn't exist
                nodes=1,
                time="00:15:00",
                partitions="cpu",
                ntasks=1,
            ),
        ),
        exec_command="srun sleep 30",
    )
)
