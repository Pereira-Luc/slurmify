from utils.config_info import Job, System, Jobs, Resources

Jobs = Jobs()

Jobs.add_job(
    Job(
        name="TimeLimitExceededJob",
        system=System(
            name="ExcessiveTimeSystem",
            resources=Resources(
                account="lxp",
                cores=4,
                gpu=None,
                mode="test",  # Test mode has limited time
                nodes=1,
                time="100:00:00",  # Error: Exceeds test mode time limit
                partitions="cpu",
                ntasks=1,
            ),
        ),
        exec_command="srun sleep 30",
    )
)
