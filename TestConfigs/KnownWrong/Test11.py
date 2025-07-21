from utils.config_info import Job, System, Jobs, Resources

Jobs = Jobs()

Jobs.add_job(
    Job(
        name="ExcessiveResourceJob",
        system=System(
            name="TooManyNodesSystem",
            resources=Resources(
                account="lxp",
                cores=128,
                gpu=None,
                mode="default",
                nodes=10,  # Error: Requesting multiple nodes but only one task
                time="00:15:00",
                partitions="cpu",
                ntasks=1,
            ),
        ),
        exec_command="srun sleep 30",
    )
)
