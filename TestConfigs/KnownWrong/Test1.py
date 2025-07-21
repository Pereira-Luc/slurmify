from utils.config_info import Job, System, Jobs, Resources

Jobs = Jobs()

Jobs.add_job(
    Job(
        name="InvalidPartitionJob",
        system=System(
            name="BadPartitionSystem",
            resources=Resources(
                account="lxp",
                cores=1,
                gpu=None,
                mode="gpu",
                nodes=1,
                time="00:15:00",
                partitions="invalid_partition",  # Error: This partition doesn't exist
                ntasks=1,
            ),
        ),
        exec_command=["srun sleep 30"],
    )
)
