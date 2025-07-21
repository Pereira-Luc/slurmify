# Example 13: Complex multi-node job for LLM training
from utils.config_info import Jobs, Job, System, Resources, Environment, Modules, Module

Jobs = Jobs()

# Create environment for LLM training
llm_env = Environment(
    name="LLM_ENV",
    commands=[
        "export NCCL_DEBUG=INFO",
        "export NCCL_IB_DISABLE=0",
        "export NCCL_SOCKET_IFNAME=^docker0,lo",
        "export MASTER_ADDR=$(hostname -I | awk '{print $1}')",
        "export MASTER_PORT=29500",
        "export WORLD_SIZE=${SLURM_NTASKS}",
        "export LOCAL_RANK=${SLURM_LOCALID}",
        "export RANK=${SLURM_PROCID}",
    ],
)

Jobs.add_job(
    Job(
        name="LLMTraining",
        system=System(
            name="LLMSystem",
            resources=Resources(
                account="lxp",
                cores=48,
                gpu=4,
                mode="large",
                nodes=4,
                time="48:00:00",
                partitions="gpu",
                ntasks=4,
            ),
        ),
        environments=[llm_env],
        modules=Modules(
            list_of_modules=[
                Module(name="PyTorch/2.1.2-foss-2023a-CUDA-12.1.1"),
                Module(name="Transformers/4.44.0-gfbf-2024a"),
            ]
        ),
        exec_command=[
            "srun --ntasks-per-node=1 --gpu-bind=closest python -m torch.distributed.run --nproc_per_node=4 --nnodes=4 train_llm.py"
        ],
    )
)
