# Missing the "from utils.config_info import" line
# This will cause a NameError when trying to use the classes

Jobs = Jobs()  # NameError: name 'Jobs' is not defined

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
                time="00:15:00",
                partitions="cpu",
                ntasks=1,
            ),
        ),
        exec_command="srun echo 'Hello World'",
    )
)
