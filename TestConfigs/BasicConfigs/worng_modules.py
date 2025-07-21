from sys import modules
from utils.config_info import Job, System, Jobs, Resources, Modules, Module

Jobs = Jobs()

modules_list = [Module(name="PyTorch")]
modules = Modules(list_of_modules=modules_list)

Jobs.add_job(
    Job(
        name="InvalidPartitionJob",
        system=System(
            name="BadPartitionSystem",
            resources=Resources(
                account="lxp",
                cores=1,
                gpu=None,
                mode="gpu",
                nodes=1,
                time="00:15:00",
                partitions="cpu",  # Error: This partition doesn't exist
                ntasks=1,
            ),
        ),
        modules=modules,
        exec_command=["srun sleep 30"],
    )
)
