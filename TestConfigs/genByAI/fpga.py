# Example 8: Set up a job with time constraint for an FPGA partition
from utils.config_info import Jobs, Job, System, Resources

Jobs = Jobs()

Jobs.add_job(
    Job(
        name="FPGAJob",
        system=System(
            name="FPGASystem",
            resources=Resources(
                account="lxp",
                cores=32,
                mode="default",
                nodes=1,
                time="12:00:00",
                partitions="fpga",  # Using the FPGA partition
                ntasks=1,
            ),
        ),
        exec_command=["srun ./fpga_application"],
    )
)
