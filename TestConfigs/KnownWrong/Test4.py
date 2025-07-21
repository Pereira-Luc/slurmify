from utils.config_info import Job, System, Jobs, Resources

Jobs = Jobs()

Jobs.add_job(
    Job(
        name="ExcessiveResourceJob",
        system=System(
            name="TooManyNodesSystem",
            resources=Resources(
                account="lxp",
                cores=256,
                gpu=None,
                mode="default",
                nodes=1000,  # Error: Requesting too many nodes
                time="00:15:00",
                partitions="cpu",
                ntasks=1000,
            ),
        ),
        exec_command="srun sleep 30",
    )
)
