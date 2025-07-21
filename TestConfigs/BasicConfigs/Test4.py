from utils.config_info import Job, System, Jobs, Resources

Jobs = Jobs()

Jobs.add_job(
    Job(
        name="SleepJob4",
        system=System(
            name="GPUSystem",
            resources=Resources(
                account="lxp",
                cores=16,
                gpu=1,
                mode="default",
                nodes=1,
                time="00:30:00",
                partitions="gpu",
                ntasks=1,
            ),
        ),
        exec_command="srun sleep 30",
    )
)
