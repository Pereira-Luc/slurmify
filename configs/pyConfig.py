from utils.config_info import (
    Job,
    Environment,
    System,
    Jobs,
    Resources,
    Logs,
    Modules,
    Module,
)

python_env = Environment(
    name="PyEnv",
    commands=["pip install -r requirements.txt", "python setup.py install"],
)

shell_export = Environment(
    name="Exports", commands=["export PATH=/some/path:$PATH", "export VAR=value"]
)

main_system = System(
    name="Program",
    resources=Resources(account="lxp", cores=0, gpu=1, mode="default", nodes=2),
)

database_system = System(
    name="DataBase",
    resources=Resources(account="lxp", cores=1, gpu=-1, mode="default", nodes=1),
)

main_job = Job(
    name="MainJob",
    environments=[python_env, shell_export],
    system=main_system,
    logs=Logs(default="logs_Path", error="error_logs_Path"),
    modules=Modules(list_of_modules=[Module(name="module0"), Module(name="module1")]),
    exec_command="srun",
)

sub_job = Job(
    name="Def", environments=[python_env], system=database_system, exec_command="srun"
)

Jobs = Jobs()
Jobs.add_job(main_job)
Jobs.add_job(sub_job)
