from utils.config_info import Job, System, Jobs, Resources

Jobs = Jobs()

Jobs.add_job(
    Job(
        name="SleepJob5",
        system=System(
            name="LongRunSystem",
            resources=Resources(
                account="lxp",
                cores=8,
                gpu=None,
                mode="long",
                nodes=1,
                time="120:00:00",
                partitions="cpu",
                ntasks=1,
            ),
        ),
        exec_command="srun sleep 30",
    )
)
