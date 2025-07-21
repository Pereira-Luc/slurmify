from utils.config_info import (
    Job,
    Environment,
    System,
    Jobs,
    Resources,
    Logs,
)


class NodePool:
    def __init__(self, name: str, node_count: int):
        self.name = name
        self.node_count = node_count


class CPUSet:
    def __init__(self, nodes: NodePool, cpu_per_node: int, cpus_per_task: int):
        self.nodes = nodes
        self.cpu_per_node = cpu_per_node
        self.cpus_per_task = cpus_per_task


data = {
    "jobs": [
        {
            "nodes": 10,
            "cores_per_node": 20,
            "name": "main_job",
            "command": "srun python ./main.py",
        },
        {
            "nodes": 1,
            "cores_per_node": 4,
            "name": "frontend_job",
            "command": "srun python ./frontend.py",
        },
    ]
}

# Change the variable name to 'Jobs'
Jobs = Jobs()

# Define resources for the large job
nodes_20 = NodePool("node_pool", node_count=10)
cpuset_large = CPUSet(nodes=nodes_20, cpu_per_node=20, cpus_per_task=1)

large_resources = Resources(
    account="lxp", partitions="cpu", cores=20 * 1
)  # Example values
large_logs = Logs(
    default=f"{data['jobs'][0]['name']}-slurm-%j.out",
    error=f"{data['jobs'][0]['name']}-slurm-%j.err",
)
large_job = Job(
    name=data["jobs"][0]["name"],
    system=System(resources=large_resources),
    exec_command=data["jobs"][0]["command"],  # Use exec_command
    logs=large_logs,
)
Jobs.add_job(large_job)

# Define resources for the small job
nodes_4 = NodePool("node_pool", node_count=1)
cpuset_small = CPUSet(nodes=nodes_4, cpu_per_node=4, cpus_per_task=1)

small_resources = Resources(account="lxp", partitions="cpu", cores=4)  # Example values
small_logs = Logs(
    default=f"{data['jobs'][1]['name']}-slurm-%j.out",
    error=f"{data['jobs'][1]['name']}-slurm-%j.err",
)
# Create and add small_job to jobs list using exec_command instead of command
small_job = Job(
    name=data["jobs"][1]["name"],
    system=System(resources=small_resources),
    exec_command=data["jobs"][1]["command"],  # Use exec_command
    logs=small_logs,
)
Jobs.add_job(small_job)
