from utils.config_info import (
    Job,
    System,
    Jobs,
    Resources,
)


Jobs = Jobs()

Jobs.add_job(  # Not sure if this works NEEEEEEDDDDSSSS TETTTEST
    Job(
        name="MinimalExample",
        system=System(
            name="lxp",
            resources=Resources(
                account="lxp",
            ),
        ),
        exec_command="srun echo 'Hello World'",
    )
)
