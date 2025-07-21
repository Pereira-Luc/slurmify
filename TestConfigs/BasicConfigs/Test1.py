from utils.config_info import Jobs, Job, System, Resources

Jobs = Jobs()

Jobs.add_job(
    Job(
        name="SleepJob1",
        system=System(
            name="CPUSystem",
            resources=Resources(
                account="lxp",
                cores=1,
                gpu=None,
                mode="default",
                nodes=1,
                time="00:30:00",
                partitions="cpu",
                ntasks=1,
            ),
        ),
        exec_command=["srun sleep 30"],
    )
)
