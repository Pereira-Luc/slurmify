from utils.printers import print_info
from utils.slurmifyValidationReport import ErrorEntry
from errorMsgs.func import (
    get_class_from_name,
    get_class_type_hints,
    get_all_valid_classes,
)
import re


def syntaxErrorMsg(e: SyntaxError) -> ErrorEntry:
    """
    Handle syntax errors in the configuration file.

    Args:
        error (SyntaxError): The syntax error to handle.

    Returns:
        ErrorEntry: An error entry with the details of the syntax error.
    """
    return ErrorEntry(
        critical=True,
        msgFunctionName="syntaxErrorMsg",
        errormsg=[f"Syntax error in configuration: {str(e)}"],
        info=[
            f"Error at line {e.lineno}, column {e.offset}",
            f"Code: {e.text.strip() if e.text else 'Unknown'}",
            "Please check your Python syntax",
        ],
    )


def importErrorMsg(e: ImportError) -> ErrorEntry:
    """
    Handle import errors in the configuration file.

    Args:
        error (ImportError): The import error to handle.

    Returns:
        ErrorEntry: An error entry with the details of the import error.
    """
    return ErrorEntry(
        critical=True,
        msgFunctionName="importErrorMsg",
        errormsg=[f"Import error in configuration: {str(e)}"],
        info=[
            "This is the only correct way to import modules in Slurmify",
            "import from utils.config_info import (",
            "   Job,",
            "   Environment,",
            "   System,",
            "   Jobs,",
            "   Resources,",
            "   Logs,",
            "   Modules,",
            "   Module,",
            ")",
            f"Original error: {str(e)}",
        ],
    )


def nameErrorMsg(e: NameError) -> ErrorEntry:
    """
    Handle name errors in the configuration file.

    Args:
        error (NameError): The name error to handle.

    Returns:
        ErrorEntry: An error entry with the details of the name error.
    """

    if "not defined" in str(e):
        match = re.search(r"(?<=name ')([^']+)(?=')", str(e))
        name = match.group(0) if match else "unknown"

        # Check if the name is a class or function
        # If it is a class check if it is part or Slurmify
        # If not say so

        slurmify_classes = get_all_valid_classes()
        print_info(f"Slurmify classes: {slurmify_classes}")

        # # TODO: Get the classes dynamicalylly from the module
        # slurmify_classes = [
        #     "Job",
        #     "Environment",
        #     "System",
        #     "Jobs",
        #     "Resources",
        #     "Logs",
        #     "Modules",
        #     "Module",
        # ]

        if name in slurmify_classes:
            return ErrorEntry(
                critical=True,
                msgFunctionName="nameErrorMsg",
                errormsg=[f"Name error in configuration: {str(e)}"],
                info=[
                    f"The class '{name}' is not defined in Slurmify",
                    "Make sure to import all necessary modules",
                    "from utils.config_info import (",
                    "   Job,",
                    "   Environment,",
                    "   System,",
                    "   Jobs,",
                    "   Resources,",
                    "   Logs,",
                    "   Modules,",
                    "   Module,",
                    ")",
                    f"Original error: {str(e)}",
                ],
            )
        else:
            return ErrorEntry(
                critical=True,
                msgFunctionName="nameErrorMsg",
                errormsg=[f"Name error in configuration: {str(e)}"],
                info=[
                    f"The variable '{name}' is not defined",
                    f"{name} is not a class or function in Slurmify",
                    f"available classes: {slurmify_classes}",
                    f"Original error: {str(e)}",
                ],
            )

    return ErrorEntry(
        critical=True,
        msgFunctionName="nameErrorMsg",
        errormsg=[f"Name error in configuration: {str(e)}"],
        info=[
            "This could be due to:",
            "Misspelled variable/function name",
            "Using a variable before defining it",
            "Or missing import statements",
            "Make sure to import all necessary modules",
            f"Original error: {str(e)}",
        ],
    )


def exceptionMsg(e: Exception) -> ErrorEntry:
    """
    Handle general exceptions in the configuration file.

    Args:
        error (Exception): The exception to handle.

    Returns:
        ErrorEntry: An error entry with the details of the exception.
    """
    error_str = str(e)

    # Check if it is missing required positional arguments
    if "required positional argument" in str(e):
        return ErrorEntry(
            critical=True,
            msgFunctionName="exceptionMsg",
            errormsg=[f"Missing required positional argument: {str(e)}"],
            info=[
                "Pleas add the missing argument to your configuration",
                "Check documentation for correct parameters",
                f"Error details: {str(e)}",
            ],
        )

    if "got an unexpected keyword argument" in error_str:
        match = re.search(r"got an unexpected keyword argument '([^']+)'", error_str)
        param_name = match.group(1) if match else "unknown"
        class_name = re.search(
            r"(\w+)\.__init__\(\) got an unexpected keyword argument '(\w+)'", error_str
        )
        class_name = class_name.group(1) if class_name else None

        print_info(f"Class name: {class_name}")

        ## Reduce the printed information to the relevant classes
        if class_name is not None:
            class_hints = get_class_type_hints([get_class_from_name(class_name)])
        else:
            class_hints = get_class_type_hints()

        return ErrorEntry(
            critical=True,
            msgFunctionName="exceptionMsg",
            errormsg=[f"Unexpected keyword argument: '{param_name}'"],
            info=[
                f"The parameter '{param_name}' is not valid for this class",
                "Check documentation for correct parameters",
                *class_hints,
                f"Error details: {error_str}",
            ],
        )

    return ErrorEntry(
        critical=True,
        msgFunctionName="exceptionMsg",
        errormsg=[f"Error loading configuration: {str(e)}"],
        info=[
            "An unexpected error occurred while loading your configuration",
            f"Check documentation to see the correct way to define your configuration",
            f"Here are the available classes and their parameters:",
            *get_class_type_hints(),
            f"Error type: {type(e).__name__}",
            f"Error details: {str(e)}",
        ],
    )


def missingJobsMsg() -> ErrorEntry:
    """
    Handle missing Jobs object in the configuration file.

    Returns:
        ErrorEntry: An error entry with the details of the missing Jobs object.
    """
    return ErrorEntry(
        critical=True,
        msgFunctionName="missingJobsMsg",
        errormsg=["Missing 'Jobs' object in configuration"],
        info=[
            "Your configuration must define a 'Jobs' object",
            "import from utils.config_info import Jobs",
            "Make sure you have 'Jobs = Jobs()' in your script",
            "And that you're adding jobs with 'Jobs.add_job(...)'",
        ],
    )


def wrongJobsVariableNameMsg(names: str) -> ErrorEntry:
    """
    Handle incorrect Jobs variable name in the configuration file.

    Returns:
        ErrorEntry: An error entry with the details of the incorrect Jobs variable name.
    """
    return ErrorEntry(
        critical=True,
        msgFunctionName="wrongJobsVariableNameMsg",
        errormsg=["Jobs instance variable name must be 'Jobs'"],
        info=[
            f"Found Jobs instance(s) with incorrect variable name(s): {names}",
            "Please rename your Jobs instance to exactly 'Jobs':",
            "Jobs = Jobs()",
            "This specific name is required for correct functionality.",
        ],
    )


def missingJobMsg() -> ErrorEntry:
    """
    Handle missing Job class in the configuration file.

    Returns:
        ErrorEntry: An error entry with the details of the missing Job class.
    """
    return ErrorEntry(
        critical=True,
        msgFunctionName="missingJobMsg",
        errormsg=["Missing 'Job' class in configuration"],
        info=[
            "Your configuration must define a 'Job' class",
            "import from utils.config_info import Job",
            "Make sure you have:",
            "Job = Job(",
            '    name="MainJob",',
            "    system=System(...), # Required",
            "    environments=[Environment(...),], # Optional",
            "    logs=Logs(...), # Optional",
            "    modules=Modules(...), # Optional",
            "    exec_command='srun python my_script.py', # Required",
        ],
    )


def missingSystemMsg() -> ErrorEntry:
    """
    Handle missing System class in the configuration file.

    Returns:
        ErrorEntry: An error entry with the details of the missing System class.
    """

    return ErrorEntry(
        critical=True,
        msgFunctionName="missingSystemMsg",
        errormsg=["Missing 'System' class in configuration"],
        info=[
            "Your configuration must define a 'System' class",
            "import from utils.config_info import System",
            "Make sure you have:",
            "System = System(",
            '    name="Program",',
            "    resources=Resources(...), # Required",
            ")",
        ],
    )


def missingResourcesMsg() -> ErrorEntry:
    """
    Handle missing Resources class in the configuration file.

    Returns:
        ErrorEntry: An error entry with the details of the missing Resources class.
    """
    return ErrorEntry(
        critical=True,
        msgFunctionName="missingResourcesMsg",
        errormsg=["Missing 'Resources' class in configuration"],
        info=[
            "Your configuration must define a 'Resources' class",
            "import from utils.config_info import Resources",
            "Make sure you have:",
            "Resources = Resources(",
            '    account="lxp",',
            "    cores=4,",
            "    gpu=None,",
            "    mode='default',",
            "    nodes=1,",
            "    time='00:15:00',",
            "    partitions='cpu',",
            "    ntasks=1,",
            ")",
        ],
    )


def unexpectedKeywordMsg() -> ErrorEntry:
    """
    Handle unexpected keyword arguments in the configuration file.

    Returns:
        ErrorEntry: An error entry with the details of the unexpected keyword arguments.
    """
    return ErrorEntry(
        critical=True,
        msgFunctionName="unexpectedKeywordMsg",
        errormsg=["Unexpected keyword argument in configuration"],
        info=[
            "This could be due to:",
            "Misspelled parameter name",
            "Using a parameter that doesn't exist",
            "Check documentation for correct parameters",
        ],
    )
