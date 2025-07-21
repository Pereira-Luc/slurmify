## Good page for Information Sbatch https://docs.lxp.lu/first-steps/handling_jobs/#__tabbed_1_1
## https://docs.lxp.lu/first-steps/handling_jobs/#__tabbed_1_1
## there are also usfull slurm error messages at the bottom of the page

"""
This class is used for the configuration of the environment that will be used in the job.
The commands will not be validated in this class shell commands are expected.

Example:
    export PATH=/some/path:$PATH
    export VAR=value
    echo "Hello World" ...

The following options are mandatory: ( This can be abstracted so the user does not have to worry about it except for the account)

    time: The maximum job's running time. Once the set time is over, the job will be terminated
    account: Your project id. Format: p200000
    partition: SLURM partition (cpu, gpu, fpga, largemem)
    qos: Meluxina QOS
    nodes: Nodes to allocate
    cpus-per-task=1: Cores per task. Should be set to 1 unless you are using multithreading

Validation for qos/modes and time and some other things:
        QOS	Max. Time (hh:mm)	Max. nodes per job	Max. jobs per user	Priority	Used for..
        dev	06:00	1	1	Regular	Interactive executions for code/workflow development, with a maximum of 1 job per user; QOS linked to special reservations
        test	00:30	5%	1	High	Testing and debugging, with a maximum of 1 job per user
        short	06:00	5%	No limit	Regular	Small jobs for backfilling
        short-preempt	06:00	5%	No limit	Regular	Small jobs for backfilling
        default	48:00	25%	No limit	Regular	Standard QOS for production jobs
        long	144:00	5%	1	Low	Non-scalable executions with a maximum of 1 job per user
        large	24:00	70%	1	Regular	Very large scale executions by special arrangement, max 1 job per user, run once every two weeks (Sun)
        urgent	06:00	5%	No limit	Very high	Urgent computing needs, by special arrangement, they can preempt the 'short-preempt' QOS



Maybe using a mockup of the slurm server with docker with the actual hpc server to pre test the scripts and have even more validation

"""


class Environment:
    def __init__(self, name: str, commands: list[str]):
        self.name: str = name
        self.commands: list[str] = commands

    def __str__(self) -> str:
        return f"{self.name}: {self.commands}"


class Resources:
    def __init__(
        self,
        account: str,
        partitions: str = "cpu",
        cores: int = 1,  # This is always per task
        gpu: int | None = None,  # This is always per task
        mode: str = "default",
        nodes: int | None = None,
        time: str = "00:15:00",
        ntasks: int = 1,
    ) -> None:

        self.cores: int | None = cores
        self.gpu: int | None = gpu
        self.mode: str = mode
        self.nodes: int | None = nodes
        self.time: str | None = time
        self.account: str = account
        self.partitions: str = partitions
        self.ntasks: int = ntasks

    def __str__(self) -> str:
        return f"{self.cores}, {self.gpu}, {self.mode}, {self.nodes}, {self.time}, {self.account}, {self.partitions}, {self.ntasks}"


class Logs:
    def __init__(self, default: str, error: str):
        self.default: str = default
        self.error: str = error

    def __str__(self):
        return f"{self.default}, {self.error}"


class Module:
    def __init__(self, name: str):
        self.name: str = name

    def __str__(self):
        return f"{self.name}"


class Modules:
    def __init__(self, list_of_modules: list[Module] = []):
        self.modules: list[Module] = list_of_modules

    def add_module(self, module: Module):
        self.modules.append(module)

    def get_modules(self) -> list[Module]:
        return self.modules

    def __str__(self):
        return f"{self.modules}"


class System:
    def __init__(self, resources: Resources, name: str = None):
        self.name: str = name
        self.resources: Resources = resources

    def __str__(self):
        return f"{self.name}, {self.resources}"


"""
    This class represents one job to be executed everything inside one job will be 1 Sbatch file 
    Maybe I will do 1 sbatch per system not sure yet
"""


class Job:

    def __init__(
        self,
        name: str,
        system: System,
        exec_command: list[str],
        environments: list[Environment] | None = None,
        logs: Logs | None = None,
        modules: Modules | None = None,
    ):
        self.name: str = name
        self.environments: list[Environment] | None = environments
        self.system: System = system
        self.logs: Logs | None = logs
        self.modules: Modules | None = modules
        self.exec_command: list[str] = exec_command

    def __str__(self):
        return f"{self.name}, {self.environments}, {self.system} {self.logs}, {self.modules}, {self.exec_command}"


class Jobs:
    def __init__(self, jobs=None):
        if jobs is None:
            jobs = []
        self.jobs: list[Job] = jobs

    def add_job(self, job: Job):
        self.jobs.append(job)

    def get_jobs(self) -> list[Job]:
        return self.jobs

    def clear_jobs(self):
        self.jobs.clear()

    # This function is a placeholder for generating a job based on the number of CPUs
    # and all other parameters that are needed to generate the job.
    def generate_job_based_on_params(
        self,
        name: str,
        account: str,
        exec_command: list[str],
        cores: int = 1,
        gpu: int | None = None,
        mode: str = "default",
        nodes: int | None = None,
        time: str = "00:15:00",
        ntasks: int = 1,
        partition: str = "cpu",
        environment_commands: list[str] | None = None,
        module_names: list[str] | None = None,
        logs_default: str | None = None,
        logs_error: str | None = None,
    ) -> Job:
        """
        Generate a job based on the provided parameters.

        Args:
            name: Name of the job
            account: Project account ID
            exec_command: Command to execute
            cores: Number of CPU cores per task (default: 1)
            gpu: Number of GPUs per task (default: None)
            mode: QoS mode (default: "default")
            nodes: Number of nodes (default: None)
            time: Maximum runtime in "HH:MM:SS" (default: "00:15:00")
            ntasks: Number of tasks (default: 1)
            partition: Slurm partition (default: "cpu")
            environment_commands: List of environment setup commands (default: None)
            module_names: List of module names to load (default: None)
            logs_default: Path for stdout logs (default: None)
            logs_error: Path for stderr logs (default: None)

        Returns:
            Job: The generated job instance
        """

        resources = Resources(
            account=account,
            partitions=partition,
            cores=cores,
            gpu=gpu,
            mode=mode,
            nodes=nodes,
            time=time,
            ntasks=ntasks,
        )

        system = System(resources=resources, name=None)  # Name is optional

        # Logs - only if either logs_default or logs_error is provided
        logs = None
        if logs_default is not None or logs_error is not None:
            # Use defaults if only one is provided
            default_log = logs_default if logs_default is not None else "job-%j.out"
            error_log = logs_error if logs_error is not None else "job-%j.err"
            logs = Logs(default=default_log, error=error_log)

        # Environment - only if environment_commands provided
        environments = None
        if environment_commands:
            environments = [
                Environment(name=f"Env_{name}", commands=environment_commands)
            ]

        # Modules - only if module_names provided
        modules = None
        if module_names:
            modules_list = [Module(name=module_name) for module_name in module_names]
            modules = Modules(list_of_modules=modules_list)

        # Create Job object
        job = Job(
            name=name,
            system=system,
            exec_command=exec_command,
            environments=environments,
            logs=logs,
            modules=modules,
        )

        # Add job to jobs list
        self.add_job(job)

        return job


def available_classes():
    """
    This function will return all the classes that are available in this module.
    It will return a list of tuples with the class name and the class itself.
    """
    classes = []
    for name, obj in globals().items():
        if isinstance(obj, type):
            classes.append((name, obj))
    return classes
