from utils.config_info import Job, System, Jobs, Resources

# Create a Jobs collection
Jobs = Jobs()

# Define MainJob with 10 nodes each with 20 cores
main_job = Job(
    name="MainJob",
    system=System(
        name="Program",
        resources=Resources(
            account="lxp",
            nodes=10,
            cores=20,
            time="02:00:00",  # 2 hours runtime for main job
        ),
    ),
    exec_command="srun python ./main.py",  # Command to execute
)

# Define FrontendJob with 1 node and 4 cores
frontend_job = Job(
    name="FrontendJob",
    system=System(
        name="Program",
        resources=Resources(
            account="lxp",
            nodes=1,
            cores=4,
            time="01:00:00",  # 1 hour runtime for frontend job
        ),
    ),
    exec_command="srun python ./frontend.py",  # Command to execute
)

# Add jobs to the Jobs collection
Jobs.add_job(main_job)
Jobs.add_job(frontend_job)
