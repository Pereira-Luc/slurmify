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

Jobs = Jobs()


Jobs.add_job(  # Not sure if this works NEEEEEEDDDDSSSS TETTTEST
    Job(
        name="MainJob",
        system=System(
            name="Program",
            resources=Resources(
                cores=128,
                gpu=1,
                mode="defadwult",
                nodes=-1,
                account="lxp",
                ntasks=1,
                time="00:10",
                partitions="gpu",
            ),
        ),
        environments=[  ## Will be made optional
            Environment(
                name="PyEnv",
                commands=["pip install -r requirements.txt", "python setup.py install"],
            )
        ],
        logs=Logs(  ## Will be made optional
            default="logs_Path", error="error_logs_Path"
        ),
        modules=Modules(  ## Will be made optional
            list_of_modules=[
                Module(name="module0"),
                Module(name="module1"),
            ]  # Maybe I will remove the module class since is kind of useless
        ),
        exec_command="srun ...",  ## maybe make will make it a list
    )
)
