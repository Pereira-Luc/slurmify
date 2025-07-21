from utils.config_info import Job, System, Jobs, Resources

Jobs = Jobs()

Jobs.add_job(
    Job(
        name="WrongTypesJob",
        system=System(
            name="TypeErrorSystem",
            resources=Resources(
                account="lxp",
                cores="all",  # Error: String instead of int
                gpu=None,
                mode="default",
                nodes="one",  # Error: String instead of int
                time="00:15:00",
                partitions="cpu",
                ntasks=1,
            ),
        ),
        exec_command="srun sleep 30",
    )
)
