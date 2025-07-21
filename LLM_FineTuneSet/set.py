fine_tune_set = {
    "ex1": {
        "input": ["Can you create a Slurmify config that uses 10 cpus to run main.py?"],
        "output": [
            """from utils.config_info import Jobs, Job, System, Resources

            Jobs = Jobs()

            Jobs.add_job(
                Job(
                    name="SleepJob1",
                    system=System(
                        name="CPUSystem",
                        resources=Resources(
                            account="lxp",
                            cores=10,
                            mode="default",
                            nodes=1,
                            time="00:30:00",
                            partitions="cpu",
                            ntasks=1,
                        ),
                    ),
                    exec_command=["srun python main.py"],
                )
            )"""
        ],
    },
    "ex2": {
        "input": ["How do I configure a GPU job with 4 GPUs in Slurmify?"],
        "output": [
            """from utils.config_info import Jobs, Job, System, Resources

            Jobs = Jobs()

            Jobs.add_job(
                Job(
                    name="GPUJob",
                    system=System(
                        name="GPUSystem",
                        resources=Resources(
                            account="lxp",
                            cores=16,
                            gpu=4,
                            mode="default",
                            nodes=1,
                            time="04:00:00",
                            partitions="gpu",
                            ntasks=1,
                        ),
                    ),
                    exec_command=["srun python gpu_script.py"],
                )
            )"""
        ],
    },
    "ex3": {
        "input": [
            "What's wrong with this Slurmify configuration?",
            """from utils.config_info import Job, System, Jobs, Resources
                  
                  Jobs = Jobs()
                  
                  Jobs.add_job(
                      Job(
                          name="InvalidTimeJob",
                          system=System(
                              name="BadTimeSystem",
                              resources=Resources(
                                  account="lxp",
                                  cores=4,
                                  gpu=None,
                                  mode="default",
                                  nodes=1,
                                  time="24h",  # This time format is incorrect
                                  partitions="cpu",
                                  ntasks=1,
                              ),
                          ),
                          exec_command="srun sleep 30",
                      )
                  )""",
        ],
        "output": [
            "The Slurmify configuration has an invalid time format. In Slurmify, the time parameter should follow the format 'HH:MM:SS' for hours, minutes, and seconds, or 'DD-HH:MM:SS' for days, hours, minutes, and seconds. The current format '24h' is invalid. It should be changed to something like '24:00:00' for 24 hours."
        ],
    },
    "ex4": {
        "input": ["How do I set up a job that loads Python and CUDA modules?"],
        "output": [
            """from utils.config_info import Jobs, Job, System, Resources, Modules, Module

            Jobs = Jobs()

            Jobs.add_job(
                Job(
                    name="ML_Training",
                    system=System(
                        name="ML_System",
                        resources=Resources(
                            account="lxp",
                            cores=8,
                            gpu=1,
                            mode="default",
                            nodes=1,
                            time="08:00:00",
                            partitions="gpu",
                            ntasks=1,
                        ),
                    ),
                    modules=Modules(
                        list_of_modules=[
                            Module(name="Python/3.9"),
                            Module(name="CUDA/11.7")
                        ]
                    ),
                    exec_command=["srun python train_model.py"],
                )
            )"""
        ],
    },
    "ex5": {
        "input": ["How do I create a multi-node job in Slurmify?"],
        "output": [
            """from utils.config_info import Jobs, Job, System, Resources

            Jobs = Jobs()

            Jobs.add_job(
                Job(
                    name="MultiNodeJob",
                    system=System(
                        name="DistributedSystem",
                        resources=Resources(
                            account="lxp",
                            cores=32,
                            gpu=None,
                            mode="default",
                            nodes=4,  # Request 4 nodes
                            time="12:00:00",
                            partitions="cpu",
                            ntasks=4,  # Important: match number of nodes for distributed tasks
                        ),
                    ),
                    exec_command=["srun -n 4 --nodes=4 python distributed_script.py"],
                )
            )"""
        ],
    },
    "ex6": {
        "input": [
            "How can I create a job with specific environment variables in Slurmify?"
        ],
        "output": [
            """from utils.config_info import Jobs, Job, System, Resources, Environment

            Jobs = Jobs()

            # Define the environment setup
            env_setup = Environment(
                name="ML_ENV",
                commands=[
                    "export PYTHONPATH=$PYTHONPATH:/path/to/libraries",
                    "export OMP_NUM_THREADS=4",
                    "export CUDA_VISIBLE_DEVICES=0,1"
                ],
            )

            Jobs.add_job(
                Job(
                    name="EnvJob",
                    system=System(
                        name="EnvSystem",
                        resources=Resources(
                            account="lxp",
                            cores=8,
                            gpu=2,
                            mode="default",
                            nodes=1,
                            time="02:00:00",
                            partitions="gpu",
                            ntasks=1,
                        ),
                    ),
                    environments=[env_setup],
                    exec_command=["srun python script_with_env.py"],
                )
            )"""
        ],
    },
    "ex7": {
        "input": ["How do I set up custom log files in Slurmify?"],
        "output": [
            """from utils.config_info import Jobs, Job, System, Resources, Logs

            Jobs = Jobs()

            # Define custom log paths
            custom_logs = Logs(
                default="job_%j_output.log",  # %j will be replaced with the job ID
                error="job_%j_error.log",
            )

            Jobs.add_job(
                Job(
                    name="LoggingJob",
                    system=System(
                        name="LogSystem",
                        resources=Resources(
                            account="lxp",
                            cores=4,
                            gpu=None,
                            mode="default",
                            nodes=1,
                            time="01:00:00",
                            partitions="cpu",
                            ntasks=1,
                        ),
                    ),
                    logs=custom_logs,
                    exec_command=["srun python script_with_logs.py"],
                )
            )"""
        ],
    },
    "ex8": {
        "input": ["How do I set up a job for FPGA usage in Slurmify?"],
        "output": [
            """from utils.config_info import Jobs, Job, System, Resources

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
            )"""
        ],
    },
    "ex9": {
        "input": [
            "How do I configure a job with large memory requirements in Slurmify?"
        ],
        "output": [
            """from utils.config_info import Jobs, Job, System, Resources

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
            )"""
        ],
    },
    "ex10": {
        "input": [
            "How can I create a job using Ray for distributed computing in Slurmify?"
        ],
        "output": [
            """from utils.config_info import Jobs, Job, System, Resources, Environment

            Jobs = Jobs()

            ray_env = Environment(
                name="RAY_ENV",
                commands=[
                    "export HEAD_HOSTNAME=$(hostname)",
                    "export HEAD_IP=$(hostname --ip-address)",
                    "export PORT=6379",
                    'export RAY_HEAD_CMD="ray start --head --port=$PORT"',
                    'export RAY_WORKER_CMD="ray start --address=$HEAD_IP:$PORT"',
                ],
            )

            Jobs.add_job(
                Job(
                    name="RayDistributed",
                    system=System(
                        name="RaySystem",
                        resources=Resources(
                            account="lxp",
                            cores=32,
                            gpu=4,
                            mode="default",
                            nodes=2,
                            time="24:00:00",
                            partitions="gpu",
                            ntasks=2,
                        ),
                    ),
                    environments=[ray_env],
                    exec_command=[
                        'srun --nodes=1 --ntasks=1 -w $HEAD_HOSTNAME bash -c "$RAY_HEAD_CMD" &',
                        "sleep 10",
                        'srun --nodes=1 --ntasks=1 --exclude=$HEAD_HOSTNAME bash -c "$RAY_WORKER_CMD" &',
                        "sleep 5",
                        "srun --nodes=1 --ntasks=1 -w $HEAD_HOSTNAME python ray_script.py",
                    ],
                )
            )"""
        ],
    },
    "ex11": {
        "input": ["How do I configure an urgent job with high priority in Slurmify?"],
        "output": [
            """from utils.config_info import Jobs, Job, System, Resources

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
            )"""
        ],
    },
    "ex12": {
        "input": [
            "How do I set up a job with development QoS for testing in Slurmify?"
        ],
        "output": [
            """from utils.config_info import Jobs, Job, System, Resources

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
            )"""
        ],
    },
}
