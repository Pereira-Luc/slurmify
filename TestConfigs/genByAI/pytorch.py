# Example 10: Job with PyTorch module for distributed training
from utils.config_info import Jobs, Job, System, Resources, Modules, Module

Jobs = Jobs()

Jobs.add_job(
    Job(
        name="DistributedTraining",
        system=System(
            name="DistributedSystem",
            resources=Resources(
                account="lxp",
                cores=32,
                gpu=4,
                mode="large",
                nodes=2,
                time="48:00:00",
                partitions="gpu",
                ntasks=2,
            ),
        ),
        modules=Modules(
            list_of_modules=[
                Module(name="PyTorch/2.1.2-foss-2023a-CUDA-12.1.1"),
                Module(name="NCCL/2.22.3-GCCcore-13.3.0-CUDA-12.6.0"),
            ]
        ),
        exec_command=[
            "srun --ntasks-per-node=1 python -m torch.distributed.run --nproc_per_node=4 --nnodes=2 training_script.py"
        ],
    )
)
