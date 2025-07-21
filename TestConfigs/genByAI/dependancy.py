# Example 12: Job with dependency on another job
from utils.config_info import Jobs, Job, System, Resources, Dependency

Jobs = Jobs()

# First job
job1 = Job(
    name="PreprocessJob",
    system=System(
        name="PreprocessingSystem",
        resources=Resources(
            account="lxp",
            cores=8,
            mode="short",
            nodes=1,
            time="01:00:00",
            partitions="cpu",
            ntasks=1,
        ),
    ),
    exec_command=["srun python preprocess.py"],
)

# Add first job
Jobs.add_job(job1)


# Second job with dependency
Jobs.add_job(
    Job(
        name="TrainingJob",
        system=System(
            name="TrainingSystem",
            resources=Resources(
                account="lxp",
                cores=16,
                gpu=2,
                mode="default",
                nodes=1,
                time="12:00:00",
                partitions="gpu",
                ntasks=1,
            ),
        ),
        dependency=Dependency(
            type="afterok",
            job_id="${SLURM_JOB_ID_PreprocessJob}",  # Reference to the first job
        ),
        exec_command=["srun python train_model.py"],
    )
)
