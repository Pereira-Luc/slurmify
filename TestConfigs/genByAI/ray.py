# Example 15: Job using Ray for distributed computing
from utils.config_info import Jobs, Job, System, Resources, Environment

Jobs = Jobs()

ray_env = Environment(
    name="RAY_ENV",
    commands=[
        "export HEAD_HOSTNAME=$(hostname)",
        "export HEAD_IP=$(hostname --ip-address)",
        "export PORT=6379",
        'export RAY_HEAD_CMD="ray start --head --port=$PORT"',
        'export RAY_WORKER_CMD="ray start --address=$HEAD_IP:$PORT"',
    ],
)

Jobs.add_job(
    Job(
        name="RayDistributed",
        system=System(
            name="RaySystem",
            resources=Resources(
                account="lxp",
                cores=32,
                gpu=4,
                mode="default",
                nodes=2,
                time="24:00:00",
                partitions="gpu",
                ntasks=2,
            ),
        ),
        environments=[ray_env],
        exec_command=[
            'srun --nodes=1 --ntasks=1 -w $HEAD_HOSTNAME bash -c "$RAY_HEAD_CMD" &',
            "sleep 10",
            'srun --nodes=1 --ntasks=1 --exclude=$HEAD_HOSTNAME bash -c "$RAY_WORKER_CMD" &',
            "sleep 5",
            "srun --nodes=1 --ntasks=1 -w $HEAD_HOSTNAME python ray_script.py",
        ],
    )
)
