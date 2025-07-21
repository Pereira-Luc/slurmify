# SLURMify Documentation

SLURMify is a tool for creating and validating SLURM job scripts using a Python-based configuration approach. This documentation explains how to use the library to define SLURM jobs with proper validation against system constraints.

## Getting Started

SLURMify allows you to create SLURM job scripts by defining Python objects that represent your job requirements. The tool handles validation and generates proper SLURM batch scripts.

## Core Components

### Job Configuration Classes

SLURMify uses the following classes from `config_info.py` to define job configurations:

- **Resources** - Define computational resource requirements
- **Environment** - Define environment setup commands
- **System** - Define system configuration (contains Resources)
- **Logs** - Define log file paths
- **Module/Modules** - Define software modules to load
- **Job** - Define a complete SLURM job
- **Jobs** - Collection of Job objects

## Creating a Configuration File

To create a SLURM job, you need to create a Python file with your job configuration:

### Minimal Example

```python
from utils.config_info import Job, System, Jobs, Resources

# Create a Jobs collection
Jobs = Jobs()

# Add a simple job
Jobs.add_job(
    Job(
        name="MinimalExample",
        system=System(
            name="lxp",
            resources=Resources(
                account="lxp",  # Your project account
            ),
        ),
        exec_command="srun echo 'Hello World'",  # Command to execute
    )
)
```

### Standard Example

```python
from utils.config_info import Job, Environment, System, Jobs, Resources, Logs, Modules, Module

# Create environment setup
python_env = Environment(
    name="PyEnv",
    commands=[
        "pip install -r requirements.txt",
        "python setup.py install"
    ]
)

# Define resources
resources = Resources(
    account="lxp",     # Your project account
    cores=128,         # CPUs per task
    gpu=4,             # GPUs per task
    mode="default",    # QoS mode
    nodes=1,           # Number of nodes
    time="2:0:0",      # Maximum runtime
    partitions="gpu"   # Partition to use
)

# Define system
my_system = System(
    name="MyProgram",
    resources=resources
)

# Define modules to load
modules = Modules(
    list_of_modules=[
        Module(name="env/release/2023.1"),
        Module(name="Apptainer/1.3.1-GCCcore-12.3.0")
    ]
)

# Define log locations
logs = Logs(
    default="job-%j.out",
    error="job-%j.err"
)

# Create job
my_job = Job(
    name="MyJob",
    environments=[python_env],
    system=my_system,
    logs=logs,
    modules=modules,
    exec_command="srun python my_script.py"
)

# Create Jobs collection and add job
Jobs = Jobs()
Jobs.add_job(my_job)
```

## Resource Options

The Resources class accepts the following parameters:

| Parameter  | Description                                | Default                |
| ---------- | ------------------------------------------ | ---------------------- |
| account    | Project account ID                         | Required               |
| partitions | SLURM partition (cpu, gpu, fpga, largemem) | "cpu"                  |
| cores      | CPUs per task                              | 1                      |
| gpu        | GPUs per task                              | None                   |
| mode       | QoS mode                                   | "default"              |
| nodes      | Number of nodes                            | None (auto-calculated) |
| time       | Maximum job runtime (HH:MM:SS)             | "00:15:00"             |
| ntasks     | Number of tasks                            | 1                      |

## QoS Modes

SLURMify supports various QoS modes with different constraints:

| QoS Mode | Max Time | Max Nodes | Description                 |
| -------- | -------- | --------- | --------------------------- |
| dev      | 06:00    | 1         | Interactive development     |
| test     | 00:30    | 5%        | Testing and debugging       |
| short    | 06:00    | 5%        | Small jobs for backfilling  |
| default  | 48:00    | 25%       | Standard production jobs    |
| long     | 144:00   | 5%        | Long-running jobs           |
| large    | 24:00    | 70%       | Very large scale executions |

## Running SLURMify

After creating your configuration file (e.g., `my_config.py`), you can generate SLURM scripts:

1. Update the path in `main.py` to point to your config file.
2. Run the main script:

   ```bash
   python main.py
   ```

The generated scripts will be placed in the `out` directory.

## Advanced Usage

For more advanced usage examples, check the sample configurations:

- `minimalTest.py` - Minimal configuration
- `pySimpleConfig.py` - Simple but complete configuration
- `complexConfig.py` - Complex example with multiple components

## Validation

SLURMify automatically validates your job configuration against system constraints:

- Checks if resources are within system limits
- Validates QoS mode and time constraints
- Ensures proper GPU allocation for GPU partitions
- Optimizes node allocation based on requested CPUs

When validation issues are detected, SLURMify will either:

- Make automatic corrections for minor issues
- Report errors for major issues that need your attention

## Example Complex Configuration

For a complete example of a multi-node GPU job, see `complexConfig.py` which demonstrates:

- Setting up a vLLM environment
- Configuring a head node with workers
- Defining environment variables and commands
- Setting up Ray for distributed processing

## Work around for unimplemented SLURM features

SLURMIfy does not implement all parameters of SLURM at least not if you need to validate them. There is a way to allow any SLURM parameter to be passed to the final script.
Environments are passed straight to the script without any validation. This allows you to pass any SLURM parameter to the script. This is not recommended as it bypasses the validation process and can lead to errors in your job submission. This only works for SLURMIfy configuration files not In the webUI since the webUI uses RestAPI to submit jobs and does not allow any SLURM parameters to be passed.

## SLURMify Parameters

SLURMify provides a flexible command-line interface with various options:

### Basic Usage

| Parameter           | Description                                           |
| ------------------- | ----------------------------------------------------- |
| `-f, --file`        | Path to the Python configuration file                 |
| `-I, --init`        | Generate a new configuration file at specified path   |
| `-o, --output`      | Output file path for the generated SLURM script       |
| `-t, --test`        | Run in testing mode                                   |
| `-v, --verbose`     | Enable verbose output                                 |
| `--validation-only` | Only validate configuration without generating script |

### Mode Options

| Parameter | Description               |
| --------- | ------------------------- |
| `--web`   | Enable web interface mode |
| `--api`   | Enable API mode           |

### Module Management

| Parameter              | Description                              |
| ---------------------- | ---------------------------------------- |
| `--module-search`      | Search for a module in the module list   |
| `--create-module-list` | Create a module list from the HPC system |

### Generate Command

The `generate` subcommand creates SLURM scripts directly from command-line parameters:

```bash
slurmify generate --name myjob --account p200000 --command "srun python script.py"
```

#### Required Parameters for Generate

| Parameter   | Description                                        |
| ----------- | -------------------------------------------------- |
| `--name`    | Name of the job                                    |
| `--account` | Project account ID (e.g., p200000)                 |
| `--command` | Command to execute (e.g., 'srun python script.py') |

#### Resource Parameters for Generate

| Parameter     | Description                | Default    |
| ------------- | -------------------------- | ---------- |
| `--partition` | SLURM partition to use     | "cpu"      |
| `--cores`     | CPUs per task              | 1          |
| `--nodes`     | Number of nodes            | 1          |
| `--ntasks`    | Number of tasks            | 1          |
| `--gpu`       | GPUs per task              | None       |
| `--qos`       | Quality of service mode    | "default"  |
| `--time`      | Maximum runtime (HH:MM:SS) | "00:15:00" |

#### Optional Parameters for Generate

| Parameter        | Description                                         | Default             |
| ---------------- | --------------------------------------------------- | ------------------- |
| `--logs-default` | Path for stdout logs                                | "slurmify-%j.out"   |
| `--logs-error`   | Path for stderr logs                                | "slurmify-%j.err"   |
| `--env`          | Environment setup commands (can use multiple times) | None                |
| `--module`       | Modules to load (can use multiple times)            | None                |
| `--output`       | Output file path                                    | ./out/<job_name>.sh |

### Examples

Generate a SLURM script from a configuration file:

```bash
python main.py -f configs/my_config.py
```

Generate a new configuration template:

```bash
python main.py --init new_config.py
```

Generate a SLURM script directly with parameters:

```bash
python main.py generate --name test-job --account p200000 --partition gpu --gpu 4 --time 1:00:00 --command "srun python train.py" --module "env/release/2023.1" --module "CUDA/12.0.1"
```

Validate a configuration file without generating a script:

```bash
python main.py -f configs/my_config.py --validation-only
```

## Testing

SLURMify includes a set of test configurations to ensure the library works as expected. You can run the tests using:

```bash
python main.py -t
```

## Web Interface

SLURMify provides a web interface for job submission. You can access it by running:

```bash
./run.sh
```

This will start the API required for the AI Agent and the web interface. You can then access the web UI at `http://localhost:8501`.

The script is mostly to run as a service not for local usage. It will start the web interface on port 8501 by default. You can also run it with the `--web` option to enable the web interface mode only.

```bash
poython main.py --web
```

The Api can be run in the same way:

```bash
python main.py --api
```
