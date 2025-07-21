from utils.config_info import Job, System, Jobs, Resources

Jobs = Jobs()

Jobs.add_job(
    Job(
        name="SleepJob6",
        system=System(
            name="MultiGPUSystem",
            resources=Resources(
                account="lxp",
                cores=32,
                gpu=2,
                mode="default",
                nodes=1,
                time="01:00:00",
                partitions="gpu",
                ntasks=2,
            ),
        ),
        exec_command="srun sleep 30",
    )
)
