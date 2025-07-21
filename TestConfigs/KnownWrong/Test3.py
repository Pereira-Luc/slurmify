from utils.config_info import Job, System, Jobs, Resources

Jobs = Jobs()

Jobs.add_job(
    Job(
        name="NegativeNodesJob",
        system=System(
            name="NegativeNodeSystem",
            resources=Resources(
                account="lxp",
                cores=4,
                gpu=None,
                mode="default",
                nodes=-5,  # Error: Negative node count
                time="00:15:00",
                partitions="cpu",
                ntasks=1,
            ),
        ),
        exec_command="srun sleep 30",
    )
)
