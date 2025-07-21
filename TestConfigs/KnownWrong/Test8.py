from utils.config_info import Job, System, Jobs, Resources

Jobs = Jobs()

Jobs.add_job(
    Job(
        name="GPUWithoutGPUPartitionJob",
        system=System(
            name="MismatchedResourceSystem",
            resources=Resources(
                account="lxp",
                cores=4,
                gpu=2,  # Requesting GPUs...
                mode="default",
                nodes=1,
                time="00:15:00",
                partitions="cpu",  # ...but on CPU partition
                ntasks=1,
            ),
        ),
        exec_command="srun sleep 30",
    )
)
