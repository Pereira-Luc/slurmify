import argparse
from utils.config_getters import get_valid_modes, get_valid_partitions


def arg_handler():
    parser = argparse.ArgumentParser(
        description="SLURMify - Generate SLURM scripts from Python configurations"
    )

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Original arguments for backward compatibility
    parser.add_argument(
        "-f",
        "--file",
        type=str,
        help="Path to the Python configuration file",
    )
    parser.add_argument(
        "-I",
        "--init",
        type=str,
        help="Generate a new configuration file at the specified path",
        metavar="FILENAME",
    )
    parser.add_argument(
        "-t",
        "--test",
        action="store_true",
        help="Run in testing mode",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    parser.add_argument(
        "--web",
        action="store_true",
        help="Enable web mode ",
    )
    parser.add_argument(
        "--module_search",
        type=str,
        help="Search for a module in the module list (TODO)",
    )
    parser.add_argument(
        "--create-module-list",
        action="store_true",
        help="Create a module list from the HPC (TODO)",
    )
    parser.add_argument(
        "--api",
        action="store_true",
        help="Enable API mode",
    )

    parser.add_argument(
        "--validation-only",
        action="store_true",
        help="Enable validation mode Only. This will not generate a SLURM script.",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Output file path for the generated SLURM script",
    )

    parser.add_argument(
        "--skip-module-check",
        action="store_true",
        help="Skip the module check when generating the SLURM script",
    )

    # Create a 'generate' subparser for generating SLURM scripts
    generate_parser = subparsers.add_parser(
        "generate", help="Generate a SLURM script with specified parameters"
    )

    # Required parameters
    generate_parser.add_argument(
        "--name", type=str, required=True, help="Name of the job"
    )
    generate_parser.add_argument(
        "--account", type=str, required=True, help="Project account ID (e.g., p200000)"
    )

    # Resource parameters
    generate_parser.add_argument(
        "--partition",
        type=str,
        default="cpu",
        choices=get_valid_partitions(),
        help="SLURM partition to use",
    )
    generate_parser.add_argument("--cores", type=int, default=1, help="CPUs per task")
    generate_parser.add_argument("--nodes", type=int, default=1, help="Number of nodes")
    generate_parser.add_argument(
        "--ntasks", type=int, default=1, help="Number of tasks"
    )
    generate_parser.add_argument("--gpu", type=int, default=None, help="GPUs per task")
    generate_parser.add_argument(
        "--qos",
        type=str,
        default="default",
        choices=get_valid_modes(),
        help="Quality of service mode",
    )
    generate_parser.add_argument(
        "--time", type=str, default="00:15:00", help="Maximum runtime (HH:MM:SS)"
    )

    # Job execution parameters
    generate_parser.add_argument(
        "--command",
        type=str,
        required=True,
        help="Command to execute (e.g., 'srun python script.py')",
    )

    # Optional parameters
    generate_parser.add_argument(
        "--logs-default",
        type=str,
        default="slurmify-%j.out",
        help="Path for stdout logs",
    )
    generate_parser.add_argument(
        "--logs-error", type=str, default="slurmiyy-%j.err", help="Path for stderr logs"
    )
    generate_parser.add_argument(
        "--env",
        type=str,
        action="append",
        help="Environment setup commands (can be used multiple times)",
    )
    generate_parser.add_argument(
        "--module",
        type=str,
        action="append",
        help="Modules to load (can be used multiple times)",
    )
    generate_parser.add_argument(
        "--output", type=str, help="Output file path (default: ./out/<job_name>.sh)"
    )

    return parser.parse_args()
