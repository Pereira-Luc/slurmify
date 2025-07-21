from utils.config_info import Job, System, Jobs, Resources, Modules, Module

Jobs = Jobs()

Jobs.add_job(
    Job(
        name="SleepJob10",
        system=System(
            name="ShortPreemptSystem",
            resources=Resources(
                account="lxp",
                cores=8,
                gpu=None,
                mode="short-preempt",
                nodes=1,
                time="04:00:00",
                partitions="cpu",
                ntasks=8,
            ),
        ),
        modules=Modules(
            list_of_modules=[Module(name="module0/test"), Module(name="module1/test")]
        ),
        exec_command="srun sleep 30",
    )
)
