import os
import yaml
from utils.config_info import Job
from utils.printers import print_debug
from utils.slurmifyValidationReport import SlurmifyValidationReport


# TODO: Extract most of the config things maybe create a class to handle the config which will make it simpler
# TODO: to retrieve the values and have some basic checks to know if the config file is wrong or not
# TODO: Some of the functions are already there but I don't use them in the other functions
# TODO: GPUS needs to be configured based on ntasks and also nodes ( Mostly done but requires to witch between different slurm --gpus-per-task and --gpus)


def load_config(config_path=None) -> dict:
    """
    Load the configuration file.

    Args:
        config_path (str, optional): Path to the configuration file.
            If None, uses the default config path.

    Returns:
        dict: The loaded configuration
    """
    if config_path is None:
        # Default to the generator config
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(current_dir, "systemConfig", "conf.yaml")

    with open(config_path, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(f"Error loading config: {exc}")
            return None


def get_valid_partitions(config=None) -> list[str]:
    """Get list of valid partitions from config."""
    if config is None:
        config: dict = load_config()

    return config["constraints"]["partitions"]


def get_valid_modes(config=None) -> list[str]:
    """Get list of valid QoS modes from config."""
    if config is None:
        config: dict = load_config()
    return config["constraints"]["modes"]


def get_partition_system_constraints(partition, config=None) -> dict | None:
    """
    Get system constraints for a specific QoS mode.

    Args:
        mode (str): QoS mode
        config (dict, optional): Config dict

    Returns:
        dict: System constraints or None if not found
    """
    if config is None:
        config: dict = load_config()

    if is_valid_partition(partition, config):
        return config["system_constraints"]["partition_details"][partition]
    return None


def get_max_cpus_partition(partition, nodes=None, config=None) -> int:
    """
    Get maximum CPUs allowed for a specific QoS mode.

    Args:
        partition (str): Partition name
        nodes (int, optional): Number of nodes
        config (dict, optional): Config dict

    Returns:
        int: Maximum allowed CPUs or None if not found
    """

    # TODO: This function is not entirely correct If ntask is 1 it can only use the cpus of one node
    if config is None:
        config: dict = load_config()

    if not is_valid_partition(partition, config):
        print(f"Invalid partition: {partition}")
        return None

    system_constraints = get_partition_system_constraints(partition, config)

    if system_constraints is None:
        return None

    if nodes is not None:
        return system_constraints["cores_per_node"] * nodes

    return system_constraints["cores_per_node"]


def get_system_partition_details(partition, config=None) -> dict | None:
    """
    Get details about a specific partition.

    Args:
        partition (str): Partition name
        config (dict, optional): Config dict

    Returns:
        dict: Partition details or None if not found
    """
    if config is None:
        config: dict = load_config()

    if partition in config["system_constraints"]["partition_details"]:
        return config["system_constraints"]["partition_details"][partition]
    return None


def is_gpu_partition(partition, config=None) -> bool:
    """
    Check if a partition is a GPU partition.

    Args:
        partition (str): Partition name
        config (dict, optional): Config dict

    Returns:
        bool: True if partition is a GPU partition
    """
    partition_details: dict | None = get_system_partition_details(partition, config)

    if partition_details is None:
        return False

    if "gpus_per_node" not in partition_details:
        print_debug(f"Partition {partition} does not have GPU details")
        return False

    return "gpus_per_node" in partition_details


def get_max_time_for_mode(mode, config=None) -> dict | None:
    """Get maximum time allowed for a specific QoS mode."""
    if config is None:
        config: dict = load_config()

    if mode in config["constraints"]["time"]:
        return config["constraints"]["time"][mode]
    return None


def calculate_max_nodes(mode, partition, config=None) -> int:
    """
    Calculate maximum nodes allowed for a mode and partition.

    Args:
        mode (str): QoS mode
        partition (str): Partition name
        config (dict, optional): Config dict

    Returns:
        int: Maximum allowed nodes or 0 if invalid
    """
    if config is None:
        config: dict = load_config()

    if mode not in config["constraints"]["max_nodes"]:
        # Dev mode will always be in the constraints
        return 1

    if partition not in config["system_constraints"]["partition_details"]:
        return 0

    total_nodes = config["system_constraints"]["partition_details"][partition]["nodes"]
    mode_restriction = config["constraints"]["max_nodes"][mode]

    return int(total_nodes * mode_restriction)


def calculate_max_gpus(mode, config=None) -> int:
    """
    Calculate maximum GPUs allowed for a mode.

    Args:
        mode (str): QoS mode
        config (dict, optional): Config dict

    Returns:
        int: Maximum allowed GPUs or 0 if invalid
    """
    if config is None:
        config = load_config()

    # Get GPU partition details
    if "gpu" not in config["system_constraints"]["partition_details"]:
        return 0

    gpu_partition: dict = config["system_constraints"]["partition_details"]["gpu"]
    total_nodes: int = gpu_partition["nodes"]
    gpus_per_node: int = gpu_partition["gpus_per_node"]

    if mode not in config["constraints"]["max_nodes"]:
        return int(1 * gpus_per_node)

    mode_restriction = config["constraints"]["max_nodes"][mode]
    allowed_nodes = int(total_nodes * mode_restriction)

    return int(allowed_nodes * gpus_per_node)


def get_slurm_translation(attribute, config=None):
    """
    Get SLURM command translation for a Python attribute.

    Args:
        attribute (str): Python attribute name
        config (dict, optional): Config dict

    Returns:
        str: SLURM command option or None if not found
    """
    if config is None:
        config: dict = load_config()

    slurm_info = config["SlurmInfo"]

    if attribute in slurm_info:
        return slurm_info[attribute]

    # Check for nested attributes (like logs.default)
    for key, value in slurm_info.items():
        if isinstance(value, dict) and attribute in value:
            return value[attribute]

    return None


def is_valid_partition(partition, config=None):
    """Check if partition is valid."""
    return partition in get_valid_partitions(config)


def is_valid_mode(mode, config=None):
    """Check if QoS mode is valid."""
    return mode in get_valid_modes(config)


def is_valid_time(time, mode, config=None):
    """Check if time is valid for the given mode."""
    if config is None:
        config: dict = load_config()

    max_time = get_max_time_for_mode(mode, config)
    if max_time is None:
        return False

    # Simple string comparison should work for HH:MM:SS format
    return time <= max_time


def is_valid_node_count(nodes, mode, partition, config=None):
    """Check if node count is valid for the given mode and partition."""
    max_nodes = calculate_max_nodes(mode, partition, config)
    return 0 < nodes <= max_nodes


def is_valid_gpu_count(gpu, mode, config=None):
    """Check if GPU count is valid for the given mode."""
    if gpu is None or gpu == 0:
        return True  # No GPU requested is valid

    max_gpus = calculate_max_gpus(mode, config)
    return 0 < gpu <= max_gpus


def calculate_max_cpus(
    cpus_per_tasks: int,
    partition: int,
    nodes: int,
    ntasks=None,
    config=None,
    report: SlurmifyValidationReport = None,
):
    """
    Calculate maximum CPUs allowed for a given node count.

    Args:
        cpus_per_node (int): CPUs per nodey
        nodes (int): Number of nodes
        config (dict, optional): Config dict

    Returns:
        int: Maximum allowed CPUs
    """
    if config is None:
        config = load_config()

    if ntasks is None:
        ntasks = 1  # Minimum Task

    if not is_valid_partition(partition, config):
        print_debug(f"Invalid partition: {partition}")
        return None

    total_cpus = get_max_cpus_partition(partition, nodes, config)
    requested_cpus: int = cpus_per_tasks * ntasks

    print_debug(f"Requested cpus: {requested_cpus}")
    print_debug(f"Total cpus: {total_cpus}")

    if total_cpus is None:
        print_debug("There was a problem with the system constraints")
        return None

    if total_cpus < requested_cpus:
        report.add_error(
            critical=True,
            errormsg=[
                "The selected amount of cpus is not possible with the current configuration"
            ],
            warning=[
                "The requested cpus are higher than the maximum cpus allowed for the selected partition"
            ],
            info=[
                f"Requested cpus: {requested_cpus}",
                f"Total cpus: {total_cpus}",
                f"If you need more cpus request more nodes or ntasks",
            ],
        )
        return None

    return total_cpus


# TODO: THIS FUNCTION CANNOT RETURN NONE NEEDS FIX
def get_min_nodes_for_cpus(cpus, partition, ntasks, config=None):
    """
    Get minimum nodes required to satisfy CPU count.

    Args:
        cpus (int): Number of CPUs
        partition (str): Partition name
        config (dict, optional): Config dict

    Returns:
        int: Minimum nodes required
    """
    if config is None:
        config = load_config()

    if not is_valid_partition(partition, config):
        print(f"Invalid partition: {partition}")
        print(f"This should be Impossible")
        exit(1)

    system_constraints = get_partition_system_constraints(partition, config)
    if system_constraints is None:
        print("There was a problem with the system constraints")
        exit(1)

    max_cpus_per_node: int = system_constraints["cores_per_node"]
    total_amount_of_cpus = ntasks * cpus

    """
        If the amount of tasks is only one the user can use only one node
    """
    if ntasks == 1:
        return 1

    return int(total_amount_of_cpus // max_cpus_per_node)
