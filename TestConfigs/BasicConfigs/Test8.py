from utils.config_info import Job, System, Jobs, Resources

Jobs = Jobs()

Jobs.add_job(
    Job(
        name="SleepJob8",
        system=System(
            name="UrgentSystem",
            resources=Resources(
                account="lxp",
                cores=16,
                gpu=None,
                mode="dev",
                nodes=1,
                time="01:00:00",
                partitions="cpu",
                ntasks=4,
            ),
        ),
        exec_command="srun sleep 30",
    )
)
