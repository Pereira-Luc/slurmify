# Example 11: Urgent job with high priority QoS
from utils.config_info import Jobs, Job, System, Resources

Jobs = Jobs()

Jobs.add_job(
    Job(
        name="UrgentAnalysis",
        system=System(
            name="UrgentSystem",
            resources=Resources(
                account="lxp",
                cores=16,
                gpu=2,
                mode="urgent",  # Using the urgent QoS
                nodes=1,
                time="06:00:00",  # Max time for urgent QoS
                partitions="gpu",
                ntasks=1,
            ),
        ),
        exec_command=["srun python urgent_analysis.py"],
    )
)
