from utils.config_info import Job, System, Resources, Jobs, Logs

# No Jobs object is created at all
# Job is created but not added to Jobs

my_job = Job(
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
    logs=Logs(),
    exec_command="srun echo 'Hello World'",
)

# Missing the Jobs = Jobs() and Jobs.add_job() calls
Jobs = Jobs()
Jobs.add_job(my_job)
