# Only importing some classes but attempting to use others
from utils.config_info import Job, Jobs

Jobs = Jobs()

# This will fail because System and Resources are not imported
Jobs.add_job(
    Job(
        name="ErrorJob",
        # Attempting to define system directly instead of using System class
        system={
            "name": "DirectSystem",
            "resources": {
                "account": "lxp",
                "cores": 4,
                "gpu": None,
                "mode": "default",
                "nodes": 1,
                "time": "00:15:00",
                "partitions": "cpu",
                "ntasks": 1,
            },
        },
        exec_command="srun echo 'Hello World'",
    )
)
