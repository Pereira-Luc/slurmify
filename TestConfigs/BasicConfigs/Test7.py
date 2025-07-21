from utils.config_info import Job, System, Jobs, Resources

Jobs = Jobs()

Jobs.add_job(
    Job(
        name="SleepJob7",
        system=System(
            name="LargeMemSystem",
            resources=Resources(
                account="lxp",
                cores=64,
                gpu=None,
                mode="default",
                nodes=1,
                time="00:45:00",
                partitions="largemem",
                ntasks=1,
            ),
        ),
        exec_command="srun sleep 30",
    )
)
