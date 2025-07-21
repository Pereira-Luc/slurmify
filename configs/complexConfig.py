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


# Define resources
resources = Resources(
    cores=128,  # --cpus-per-task=128
    gpu=4,  # --gpus-per-task=4
    mode="dev",  # -q default (qos)
    nodes=1,  # -N 5
    time="2:0:0",  # -t 2:0:0
    account="lxp",  # -A lxp
    partitions="gpu",  # -p gpu
    ntasks=2,
)

# Define modules
modules = Modules(
    list_of_modules=[
        Module(name="env/release/2023.1"),
        Module(name="Apptainer/1.3.1-GCCcore-12.3.0"),
    ]
)
"""
Example how the environment could be decomposed:

env = Environment.builder("VLLM") \
    .add_var("PMIX_MCA_psec", "native") \
    .add_path_var("LOCAL_HF_CACHE", "<Choose a path>/HF_cache") \
    .add_secure_var("HF_TOKEN", "<your HuggingFace token>") \
    .add_command("mkdir -p ${LOCAL_HF_CACHE}") \
    .build()

or something similar
"""

# Define environment setup
vllm_env = Environment(
    name="VLLM Environment",
    commands=[
        "export PMIX_MCA_psec=native",
        'export LOCAL_HF_CACHE="<Choose a path>/HF_cache"',
        "mkdir -p ${LOCAL_HF_CACHE}",
        'export HF_TOKEN="<your HuggingFace token>"',
        'export SIF_IMAGE="vllm-openai_latest.sif"',
        'export APPTAINER_ARGS=" --nvccli -B /project/home/lxp/ekieffer/HF_cache:/root/.cache/huggingface --env HF_HOME=/root/.cache/huggingface --env HUGGING_FACE_HUB_TOKEN=${HF_TOKEN}"',
        'export HF_MODEL="meta-llama/Llama-3.1-405B-FP8"',
        'export HEAD_HOSTNAME="$(hostname)"',
        'export HEAD_IPADDRESS="$(hostname --ip-address)"',
        'echo "HEAD NODE: ${HEAD_HOSTNAME}"',
        'echo "IP ADDRESS: ${HEAD_IPADDRESS}"',
        'echo "SSH TUNNEL (Execute on your local machine): ssh -p 8822 ${USER}@login.lxp.lu -NL 8000:${HEAD_IPADDRESS}:8000"',
        "export RANDOM_PORT=$(python3 -c 'import socket; s = socket.socket(); s.bind((\"\", 0)); print(s.getsockname()[1]); s.close()')",
        'export RAY_CMD_HEAD="ray start --block --head --port=${RANDOM_PORT}"',
        'export RAY_CMD_WORKER="ray start --block --address=${HEAD_IPADDRESS}:${RANDOM_PORT}"',
        "export TENSOR_PARALLEL_SIZE=4",
        "export PIPELINE_PARALLEL_SIZE=${SLURM_NNODES}",
    ],
)

# Define system
vllm_system = System(
    name="VLLM System",
    resources=resources,
)

# Define job execution command
exec_command = (
    'echo "Starting head node" && '
    'srun -J "head ray node-step-%J" -N 1 --ntasks-per-node=1 -c $(( SLURM_CPUS_PER_TASK/2 )) -w ${HEAD_HOSTNAME} '
    "apptainer exec ${APPTAINER_ARGS} ${SIF_IMAGE} ${RAY_CMD_HEAD} & "
    "sleep 10 && "
    'echo "Starting worker node" && '
    'srun -J "worker ray node-step-%J" -N $(( SLURM_NNODES-1 )) --ntasks-per-node=1 -c ${SLURM_CPUS_PER_TASK} -x ${HEAD_HOSTNAME} '
    "apptainer exec ${APPTAINER_ARGS} ${SIF_IMAGE} ${RAY_CMD_WORKER} & "
    "sleep 30 && "
    'echo "Starting server" && '
    "apptainer exec ${APPTAINER_ARGS} ${SIF_IMAGE} vllm serve ${HF_MODEL} "
    "--tensor-parallel-size ${TENSOR_PARALLEL_SIZE} --pipeline-parallel-size ${PIPELINE_PARALLEL_SIZE}"
)

# Define the VLLM job
vllm_job = Job(
    name="VLLM Job",
    environments=[vllm_env],
    system=vllm_system,
    logs=Logs(default="vllm-%j.out", error="vllm-%j.err"),
    modules=modules,
    exec_command=exec_command,
)

# Create Jobs collection and add our VLLM job
Jobs = Jobs()
Jobs.add_job(vllm_job)
