import pickle
import subprocess
import re
from numpy import test
import yaml
import os

_CLASS_MODULE_LIST = None


class ModuleList:
    """
    This class handles the module list and provides methods to access module names and versions.
    It is initialized with a dictionary containing module names as keys and their versions as values.
    """

    MODULE_LIST_CACHE = None

    def __init__(self, modules: dict[str, list[str]]):
        self.modules = modules

    def get_modules(self) -> list[str]:
        """
        Returns a list of all modules available in the module list.
        """

        # Store the module list in the cache if not already cached
        if ModuleList.MODULE_LIST_CACHE is None:
            ModuleList.MODULE_LIST_CACHE = self.modules.keys()

        return list(ModuleList.MODULE_LIST_CACHE)

    def get_module_by_name(self, module_name: str) -> dict[str, list[str]]:
        module_names = self.get_modules()
        if module_name in module_names:
            return {module_name: self.modules[module_name]}
        else:
            raise ValueError(f"Module '{module_name}' not found in the module list.")

    def get_module_versions(self, module_name: str) -> list[str]:
        """
        Returns a list of all versions available for a given module name.

        Args:
            module_name (str): Name of the module.

        Returns:
            list[str]: List of all versions available for the given module name.
        """
        return self.modules.get(module_name, [])

    def search_modules(self, search_term: str) -> list[str]:
        """
        Searches for modules that contain the given search term in their names.

        Args:
            search_term (str): The term to search for in module names.

        Returns:
            list[str]: A list of module names that match the search term.
        """
        return [
            module
            for module in self.get_modules()
            if search_term.lower() in module.lower()
        ]

    def search_modules_with_versions(self, search_term: str) -> dict[str, list[str]]:
        """
        Searches for modules that contain the given search term in their names and returns their versions.

        Args:
            search_term (str): The term to search for in module names.

        Returns:
            dict[str, list[str]]: A dictionary where keys are module names and values are lists of versions.
        """
        return {
            module: self.modules[module] for module in self.search_modules(search_term)
        }


def generate_module_list() -> list[str]:
    """
    Uses the 'module avail' command to list all available modules and extracts their names.

    Returns:
    List[str]: A list containing the names of all modules available.
    """
    try:
        # Execute the 'module spider' command
        command = "module spider"
        process = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()

        print("Getting all modules...")

        # Combine stdout and stderr into a single string
        output = stdout.decode() + stderr.decode()

        module_names = extract_module_names(output)

        # Remove duplicates by converting to a set and back to a list
        module_list = list(set(module_names))
        module_list = sorted(module_list)
        module_list = create_module_structure(module_list)

        print(f"Total modules found: {len(module_list)}")

        # Save the list to a file
        save_to_pickle(module_list, "all_modules.pkl")
        save_list_to_yaml(module_list, "all_modules.yaml")

        return module_list

    # Handle any errors that occur during the process
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def extract_module_names(output: str) -> list[str]:
    """This function extracts the names of all available modules from the output of the 'module spider' command.

    Args:
        output (str): output of the 'module spider' command.

    Returns:
        list[str]: A list containing the names of all available modules.
    """

    pattern = r"\b[A-Za-z0-9\.\-\(\)]+/[A-Za-z0-9\.\-\(\)]+\b"
    modules = re.findall(pattern, output)

    return modules


def create_module_structure(module_list: list[str]) -> dict[str, list[str]]:
    """This function creates a hierarchical structure of modules based on their names.

    Args:
        module_list (list[str]): List of module names and there versions.

    Returns:
        dict[str, list[str]]: A dictionary containing the hierarchical structure of modules.
    """

    module_structure = {}

    for module in module_list:
        parts = module.split("/")
        current_dict = module_structure

        for part in parts:
            if part not in current_dict:
                current_dict[part] = {}
            current_dict = current_dict[part]

    return module_structure


def save_list_to_yaml(module_list: list[str, list[str]], filename: str) -> None:
    """This function saves the list of modules to a YAML file.

    Args:
        module_list (list[str, list[str]]): List of modules to save.
        filename (str): Name of the file to save the list to.
    """

    with open(filename, "w") as file:
        yaml.dump(module_list, file)


def save_to_pickle(module_list: list[str, list[str]], filename: str) -> None:
    """Save module list as a binary pickle file for faster loading."""
    with open(filename, "wb") as file:
        pickle.dump(module_list, file)


def load_module_list(
    path: str = "systemConfig/all_modules",
) -> dict[str, list[str]]:
    """This function loads the module list from a YAML file.

    Args:
        filename (str): Name of the file to load the list from.

    Returns:
        dict[str, list[str]]: A dictionary containing the hierarchical structure of modules.
    """

    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, "../", path)

    # Check if file exists with pickle
    try:
        with open(path + ".pkl", "rb") as file:
            module_list = pickle.load(file)
            return module_list
    except FileNotFoundError:
        print("Pickle file not found, loading from YAML")

    # Check if file exists with YAML
    try:
        with open(path + ".yaml", "r") as file:
            module_list = yaml.safe_load(file)
            return module_list
    except FileNotFoundError:
        print("YAML file not found")
        return None


def get_module_list() -> ModuleList:
    global _CLASS_MODULE_LIST

    if _CLASS_MODULE_LIST is None:
        module_list = load_module_list()
        _CLASS_MODULE_LIST = ModuleList(module_list)

    return _CLASS_MODULE_LIST


if __name__ == "__main__":
    generate_module_list()
    # module_list = get_module_list()

    # test_search = "Python"

    # print(f"Searching for modules containing '{test_search}':")
    # search_results = module_list.search_modules(test_search)
    # print(search_results)

    # search_results_with_versions = module_list.search_modules_with_versions(test_search)
    # print(f"Modules with versions containing '{test_search}':")
    # print(search_results_with_versions)

    # print(module_list.get_module_versions("Python"))
