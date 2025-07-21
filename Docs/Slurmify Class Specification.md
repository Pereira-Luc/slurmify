# Slurmify Classes Documentation

The `slurmifyClasses.py` file defines the core data structures for the slurmify framework, a Python-based system for generating and managing Slurm job submissions on HPC clusters.

## Environment

The `Environment` class defines setup commands that are executed before the main job runs. This allows you to:

- Set up Python environments
- Export environment variables
- Perform any initialization needed for your job

```python
class Environment:
    def __init__(self, name: str, commands: list[str]):
        self.name: str = name
        self.commands: list[str] = commands
```

### Parameters:

- `name`: A descriptive identifier for this environment
- `commands`: A list of shell commands to execute before the main job

## Resources

The `Resources` class specifies the computational resources needed for a job, mapping directly to Slurm resource allocation parameters.

### Parameters:

- `account`: Billing account/project for the job
- `partitions`: Slurm partition to use (default: "cpu")
- `cores`: CPU cores per task (default: 1)
- `gpu`: GPUs per task (default: None)
- `mode`: Execution mode (default: "default")
- `nodes`: Number of compute nodes (default: None)
- `time`: Maximum runtime in HH:MM:SS format (default: "00:15:00")
- `ntasks`: Total number of tasks (default: 1)

```python
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
```

## Logs

The `Logs` class configures output and error log file paths.

```python
class Logs:
    def __init__(self, default, error):
        self.default = default
        self.error = error
```

### Parameters:

- `default`: Path for standard output logs
- `error`: Path for error logs

## Module and Modules

These classes manage software modules that need to be loaded:

- `Module`: Represents a single software module
- `Modules`: Container for multiple `Module` objects

```python
class Module:
    def __init__(self, name):
        self.name = name

class Modules:
    def __init__(self, list_of_modules=None):
        self.modules: list[Module] = list_of_modules if list_of_modules is not None else []
```

### Methods for Modules:

- `add_module(module)`: Add a module to the collection
- `get_modules()`: Retrieve all modules

## System

The `System` class combines a name with resource requirements, representing a computational environment.

```python
class System:
    def __init__(self, resources, name=None):
        self.name = name
        self.resources: Resources = resources
```

### Parameters:

- `resources`: A `Resources` object defining compute requirements
- `name`: Optional name for this system configuration

## Job

The `Job` class represents a complete Slurm job definition, combining all the configuration components.

```python
class Job:
    def __init__(
        self, name, system, exec_command, environments=None, logs=None, modules=None
    ):
        self.name: str = name
        self.environments: list[Environment] = environments
        self.system: System = system
        self.logs: Logs = logs
        self.modules: Modules = modules
        self.exec_command = exec_command
```

### Parameters:

- `name`: Job name (appears in Slurm queue)
- `system`: A `System` object defining resources
- `exec_command`: The command to execute (e.g., "srun python script.py")
- `environments`: List of `Environment` objects (optional)
- `logs`: A `Logs` object for output configuration (optional)
- `modules`: A `Modules` object for software modules (optional)

## Jobs

The `Jobs` class acts as a container for multiple `Job` objects.

```python
    class Jobs:
    def __init__(self):
        self.jobs: list[Job] = []
```

### Methods:

- `add_job(job)`: Add a job to the collection
- `get_jobs()`: Retrieve all jobs

When processed by the slurmify framework, these objects are transformed into Slurm submission scripts with the appropriate `#SBATCH` directives based on the configured resources and settings.
