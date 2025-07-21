"""
Rich interface for generating Slurmify job configurations
"""

import os
from rich.console import Console
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

# Import Slurmify classes
from utils.config_info import (
    Jobs,
    Job,
    System,
    Resources,
    Environment,
    Module,
    Modules,
    Logs,
)

console = Console()


def header():
    """Display a nice header."""
    console.print(
        Panel.fit(
            "[bold blue]Slurmify Job Generator[/bold blue]",
            border_style="blue",
            padding=(1, 2),
        )
    )
    console.print("Create a SLURM job configuration interactively")
    console.print()


def get_basic_info():
    """Collect basic job information."""
    console.print(
        Panel("[bold green]Basic Job Information[/bold green]", border_style="green")
    )

    name = Prompt.ask("[yellow]Job name[/yellow]", default="SlurmJob")
    account = Prompt.ask(
        "[yellow]Account ID[/yellow] (format: p200000)", default="default"
    )

    return name, account


def get_resources():
    """Collect resource requirements."""
    console.print(
        Panel("[bold green]Resource Requirements[/bold green]", border_style="green")
    )

    # Create a table showing partition options
    table = Table(title="Available Partitions")
    table.add_column("Partition", style="cyan")
    table.add_column("Description", style="green")

    table.add_row("cpu", "Standard CPU partition")
    table.add_row("gpu", "GPU-enabled partition")
    table.add_row("fpga", "FPGA-enabled partition")
    table.add_row("largemem", "Large memory nodes")

    console.print(table)

    partition = Prompt.ask(
        "[yellow]Partition[/yellow]",
        choices=["cpu", "gpu", "fpga", "largemem"],
        default="cpu",
    )
    cores = IntPrompt.ask("[yellow]CPU cores per task[/yellow]", default=1)

    # Only ask for GPU count if gpu partition selected
    gpu = None
    if partition == "gpu":
        gpu = IntPrompt.ask("[yellow]Number of GPUs per task[/yellow]", default=1)

    # Create a table showing QoS options
    table = Table(title="Available QoS Options")
    table.add_column("QoS", style="cyan")
    table.add_column("Max Time", style="yellow")
    table.add_column("Description", style="green")

    table.add_row("default", "48:00:00", "Standard QoS for production jobs")
    table.add_row("dev", "06:00:00", "Interactive development jobs")
    table.add_row("test", "00:30:00", "Quick testing and debugging")
    table.add_row("short", "06:00:00", "Short jobs for backfilling")
    table.add_row("long", "144:00:00", "Long-running jobs")

    console.print(table)

    qos = Prompt.ask(
        "[yellow]QoS mode[/yellow]",
        choices=[
            "default",
            "dev",
            "test",
            "short",
            "short-preempt",
            "long",
            "large",
            "urgent",
        ],
        default="default",
    )

    nodes = IntPrompt.ask("[yellow]Number of nodes[/yellow]", default=1)
    tasks = IntPrompt.ask("[yellow]Number of tasks[/yellow]", default=1)

    time_format = "HH:MM:SS"
    time = Prompt.ask(
        f"[yellow]Time limit[/yellow] (format: {time_format})", default="00:15:00"
    )

    return partition, cores, gpu, qos, nodes, tasks, time


def get_commands_and_env():
    """Get execution commands and environment setup."""
    console.print(
        Panel("[bold green]Commands & Environment[/bold green]", border_style="green")
    )

    commands = []
    console.print("[yellow]Enter execution commands (empty line to finish):[/yellow]")
    while True:
        cmd = Prompt.ask("Command", default="")
        if not cmd:
            break
        commands.append(cmd)

    if not commands:
        commands = ["echo 'No command specified'"]

    # Environment variables
    env_commands = []
    if Confirm.ask("Do you want to set environment variables?"):
        console.print(
            "[yellow]Enter environment commands (empty line to finish):[/yellow]"
        )
        while True:
            env_cmd = Prompt.ask("Environment command", default="")
            if not env_cmd:
                break
            env_commands.append(env_cmd)

    # Modules
    modules = []
    if Confirm.ask("Do you want to load modules?"):
        console.print("[yellow]Enter module names (empty line to finish):[/yellow]")
        console.print("Format: name/version (e.g., GCC/10.3.0)")
        while True:
            module = Prompt.ask("Module", default="")
            if not module:
                break
            modules.append(module)

    return commands, env_commands, modules


def get_logs():
    """Get log file configuration."""
    console.print(
        Panel("[bold green]Log Configuration[/bold green]", border_style="green")
    )

    use_logs = Confirm.ask("Do you want to specify log files?")
    if not use_logs:
        return None, None

    console.print("Default placeholders: %j (job id), %x (job name)")
    stdout = Prompt.ask(
        "[yellow]Path for standard output[/yellow]", default="job-%j.out"
    )
    stderr = Prompt.ask(
        "[yellow]Path for standard error[/yellow]", default="job-%j.err"
    )

    return stdout, stderr


def generate_config(job_params):
    """Generate a configuration file based on the collected parameters."""
    jobs = Jobs()
    job = jobs.generate_job_based_on_params(**job_params)

    # Create python configuration code
    config_code = f"""from utils.config_info import Resources, System, Job, Jobs, Environment, Module, Modules, Logs

# Create Jobs container
jobs = Jobs()

# Define resources
resources = Resources(
    account="{job_params['account']}",
    partitions="{job_params['partition']}",
    cores={job_params['cores']},
    gpu={job_params['gpu']},
    mode="{job_params['mode']}",
    nodes={job_params['nodes']},
    time="{job_params['time']}",
    ntasks={job_params['ntasks']}
)

# Create system configuration
system = System(resources=resources)

# Command to execute
exec_command = {repr(job_params['exec_command'])}
"""

    if job_params.get("logs_default") or job_params.get("logs_error"):
        config_code += f"""
# Configure logs
logs = Logs(
    default="{job_params.get('logs_default', 'job-%j.out')}",
    error="{job_params.get('logs_error', 'job-%j.err')}"
)
"""
    else:
        config_code += "\n# No log configuration specified\nlogs = None\n"

    if job_params.get("environment_commands"):
        config_code += f"""
# Configure environment
env = Environment(
    name="Env_{job_params['name']}",
    commands={repr(job_params.get('environment_commands'))}
)
environments = [env]
"""
    else:
        config_code += (
            "\n# No environment configuration specified\nenvironments = None\n"
        )

    if job_params.get("module_names"):
        config_code += f"""
# Configure modules
modules_list = [Module(name=module_name) for module_name in {repr(job_params.get('module_names'))}]
modules = Modules(list_of_modules=modules_list)
"""
    else:
        config_code += "\n# No modules specified\nmodules = None\n"

    config_code += f"""
# Create the job
job = Job(
    name="{job_params['name']}",
    system=system,
    exec_command=exec_command,
    environments=environments,
    logs=logs,
    modules=modules
)

# Add job to the Jobs collection
jobs.add_job(job)

# This variable needs to be present for Slurmify to find the jobs
Jobs = jobs
"""

    return config_code


def main():
    """Main function to run the interface."""
    header()

    # Collect all required information
    name, account = get_basic_info()
    partition, cores, gpu, qos, nodes, tasks, time = get_resources()
    commands, env_commands, modules = get_commands_and_env()
    stdout_log, stderr_log = get_logs()

    # Prepare job parameters
    job_params = {
        "name": name,
        "account": account,
        "exec_command": commands,
        "cores": cores,
        "gpu": gpu,
        "mode": qos,
        "nodes": nodes,
        "time": time,
        "ntasks": tasks,
        "partition": partition,
        "environment_commands": env_commands if env_commands else None,
        "module_names": modules if modules else None,
        "logs_default": stdout_log,
        "logs_error": stderr_log,
    }

    # Generate configuration
    config_code = generate_config(job_params)

    # Show the generated code
    console.print(
        Panel("[bold green]Generated Configuration[/bold green]", border_style="green")
    )
    syntax = Syntax(config_code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)

    # Save to file
    if Confirm.ask("Save this configuration to a file?"):
        filename = Prompt.ask(
            "Filename", default=f"{name.lower().replace(' ', '_')}_config.py"
        )
        with open(filename, "w") as f:
            f.write(config_code)
        console.print(f"[bold green]Configuration saved to {filename}[/bold green]")

        # Offer to validate
        if Confirm.ask("Validate this configuration?"):
            console.print("[bold]Running validation...[/bold]")
            import subprocess

            result = subprocess.run(
                ["python", "main.py", "--file", filename],
                capture_output=True,
                text=True,
            )
            if (
                result.returncode == 0
            ):  # TODO: This is actualy not how to check if the config is valid
                console.print("[bold green]Configuration is valid![/bold green]")
            else:
                console.print("[bold red]Configuration validation failed:[/bold red]")
                console.print(result.stdout)
                console.print(result.stderr)


if __name__ == "__main__":
    main()
