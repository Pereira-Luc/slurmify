from utils.config_info import Job, System, Jobs, Resources

Jobs = Jobs()

Jobs.add_job(
    Job(
        name="SleepJob2",
        system=System(
            name="MultiNodeSystem",
            resources=Resources(
                account="lxp",
                cores=2,
                gpu=None,
                mode="default",
                nodes=2,
                time="00:30:00",
                partitions="cpu",
                ntasks=1,
            ),
        ),
        exec_command="srun sleep 30",
    )
)
