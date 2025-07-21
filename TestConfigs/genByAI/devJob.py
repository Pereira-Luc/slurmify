# Example 14: Test job with development QoS
from utils.config_info import Jobs, Job, System, Resources

Jobs = Jobs()

Jobs.add_job(
    Job(
        name="DevTesting",
        system=System(
            name="DevSystem",
            resources=Resources(
                account="lxp",
                cores=4,
                gpu=1,
                mode="dev",  # Using dev QoS for interactive development
                nodes=1,
                time="01:00:00",  # Max 6 hours, using less
                partitions="gpu",
                ntasks=1,
            ),
        ),
        exec_command=["srun python test_development.py"],
    )
)
