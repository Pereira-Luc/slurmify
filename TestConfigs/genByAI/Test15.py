from utils.config_info import Job, Environment, System, Jobs, Resources, Logs

my_environment = Environment(
    name="my_env",
    commands=[
        "conda activate my_env",
    ],
)

main_resources = Resources(
    account="lxp",
    partitions="cpu",
    cores=20,
    nodes=10,
    time="01:00:00",
    ntasks=1,
)

frontend_resources = Resources(
    account="your_project_account",
    partitions="cpu",
    cores=4,
    nodes=1,
    time="01:00:00",
    ntasks=1,
)

main_system = System(
    resources=main_resources,
)

frontend_system = System(
    resources=frontend_resources,
)

my_logs = Logs(
    default="job-%j.out",
    error="job-%j.err",
)

main_job = Job(
    name="MainJob",
    system=main_system,
    exec_command="srun python ./main.py",
    environments=[my_environment],
    logs=my_logs,
)

frontend_job = Job(
    name="FrontendJob",
    system=frontend_system,
    exec_command="srun python ./frontend.py",
    environments=[my_environment],
    logs=my_logs,
)

Jobs = Jobs()
Jobs.add_job(main_job)
Jobs.add_job(frontend_job)
