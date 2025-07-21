from utils.config_info import Job, System, Jobs, Resources

Jobs = Jobs()

Jobs.add_job(
    Job(
        name="SleepJob3",
        system=System(
            name="ShortTestSystem",
            resources=Resources(
                account="lxp",
                cores=4,
                gpu=None,
                mode="test",
                nodes=1,
                time="00:15:00",
                partitions="cpu",
                ntasks=2,
            ),
        ),
        exec_command="srun sleep 30",
    )
)
