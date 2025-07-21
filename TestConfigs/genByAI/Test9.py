from utils.config_info import Jobs, System, Resources, Logs, Job

resources = Resources(cores="five", gpu=1, account="lxp", mode="default")

logs = Logs(default="job-%j.out", error="job-%j.err")


system = System(
    name="Program",
    resources=resources,  # Assuming you want to use the same resources for simplicity
)

my_job = Job(
    name="MyJob",
    system=system,
    exec_command="python main.py",
    logs=logs,
)


# Renaming `jobs` to `Jobs`
Jobs = Jobs()
Jobs.add_job(my_job)
