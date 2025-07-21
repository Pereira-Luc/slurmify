# Example 9: Create a job with large memory requirements
from utils.config_info import Jobs, Job, System, Resources

Jobs = Jobs()

Jobs.add_job(
    Job(
        name="BigMemoryJob",
        system=System(
            name="LargeMemSystem",
            resources=Resources(
                account="lxp",
                cores=64,
                mode="large",  # Using large QoS
                nodes=1,
                time="24:00:00",
                partitions="largemem",  # Using the large memory partition
                ntasks=1,
            ),
        ),
        exec_command=["srun python memory_intensive_analysis.py"],
    )
)
