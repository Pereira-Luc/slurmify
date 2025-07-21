from utils.config_info import Job, System, Jobs, Resources

Jobs = Jobs()

Jobs.add_job(
    Job(
        name="SleepJob9",
        system=System(
            name="FPGASystem",
            resources=Resources(
                account="lxp",
                cores=32,
                gpu=None,
                mode="default",
                nodes=1,
                time="02:00:00",
                partitions="fpga",
                ntasks=1,
            ),
        ),
        exec_command="srun sleep 30",
    )
)
