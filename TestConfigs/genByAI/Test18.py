from utils.config_info import Job, Environment, System, Jobs, Resources

resources = Resources(account="lxp", cores=0, gpu=1, mode="default", nodes=2)

Job = Job(
    name="main_job",
    system=System(Resources),
    exec_command="python main.py",
)

Jobs = Jobs()
Jobs.add_job(Job)
