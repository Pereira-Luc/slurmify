from utils.config_info import Job, System, Jobs, Resources

Jobs = Jobs()

Jobs.add_job(
    Job(
        name="ErrorJob",
        system=System(
            name="TestSystem", 
            resources=Resources(
                account="lxp",
                cores=4,
                gpu=None,
                mode="default",
                nodes=1,
                time="00:15:00"  # Missing comma here - syntax error
                partitions="cpu",
                ntasks=1,
            ),
        ),
        exec_command="srun echo 'Hello World'",
    )
)