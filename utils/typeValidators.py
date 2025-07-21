# TODO: Remove the the messages to another file

from errorMsgs.TyperErrors import missing_expected_types_ErrorMsg
from errorMsgs.func import get_expected_types
from utils.config_info import Environment, Job, Modules, Resources, System
from utils.printers import print_debug, print_error, print_info, print_warning


def check_resources_types(module, resource_instance, validation_report):
    """Check that + object has correct parameter types"""
    has_errors = False
    expected_types = get_expected_types(Resources)

    if expected_types is None:
        validation_report.add_error_entry(missing_expected_types_ErrorMsg("Resources"))
        return False

    for attr_name, expected_type in expected_types.items():
        print_debug(f"Checking {attr_name} against {expected_type}")
        attr_value = getattr(resource_instance, attr_name)

        # Handle union types (like int | None)
        if isinstance(expected_type, tuple):
            type_match = any(isinstance(attr_value, t) for t in expected_type)
        else:
            type_match = isinstance(attr_value, expected_type)

        if not type_match and attr_value is not None:
            # Special handling for None values
            if (
                isinstance(expected_type, tuple)
                and type(None) in expected_type
                and attr_value is None
            ):
                continue

            validation_report.add_error(
                critical=True,
                errormsg=[f"Resources.{attr_name} has incorrect type"],
                info=[
                    f"Expected {_format_type_name(expected_type)}, got {type(attr_value).__name__}",
                    f"Value: {attr_value}",
                ],
            )
            has_errors = True

    return not has_errors


def check_system_types(module, system_instance, validation_report):
    """Check that System object has correct parameter types"""
    has_errors = False

    expected_types = get_expected_types(system_instance)

    if expected_types is None:
        validation_report.add_error_entry(missing_expected_types_ErrorMsg("System"))
        return False

    print_info(f"System expected types: {expected_types}")

    for attr_name, expected_type in expected_types.items():

        attr_value = getattr(system_instance, attr_name)

        # Handle union types (like int | None)
        if isinstance(expected_type, tuple):
            type_match = any(isinstance(attr_value, t) for t in expected_type)
        else:
            type_match = isinstance(attr_value, expected_type)

        if not type_match and attr_value is not None:
            # Special handling for None values
            if (
                isinstance(expected_type, tuple)
                and type(None) in expected_type
                and attr_value is None
            ):
                continue
            print_error(f"System.{attr_name} has incorrect type")
            validation_report.add_error(
                critical=True,
                errormsg=[f"System.{attr_name} has incorrect type"],
                info=[
                    f"Expected {_format_type_name(expected_type)}, got {type(attr_value).__name__}",
                    f"Value: {attr_value}",
                ],
            )

            has_errors = True

        print_info(f"Checking {attr_name} against {expected_type}")
        # Special handling for resources
        if isinstance(attr_value, Resources):
            if not check_resources_types(module, attr_value, validation_report):
                print_error(f"Resources type check failed for {attr_name} in System")
                has_errors = True
            continue

    return not has_errors


def check_environments_types(module, environments_instance, validation_report):
    pass


def check_job_types(module, job_instance, validation_report):
    """Check that Job object has correct parameter types (assumes fields already exist)"""
    has_errors = False

    if not isinstance(job_instance, Job):
        validation_report.add_error(
            critical=True,
            errormsg=["Job instance is not of type Job"],
            info=[
                "Check that the Job instance is created correctly",
                "Expected type: Job",
            ],
        )
        return False

    # Get expected types from the Job class, not the instance
    expected_types = get_expected_types(job_instance.__class__)
    print_debug(f"Job expected types: {expected_types}")

    if expected_types is None:
        validation_report.add_error(
            critical=True,
            errormsg=["Unable to get expected types for Job"],
            info=[
                "Check that the Job class is defined correctly",
                "Expected types could not be determined",
            ],
        )
        return False

    # Validate each attribute that has type information
    for attr_name, expected_type in expected_types.items():
        # Skip if attribute doesn't exist - this is chec
        # ked by other validators
        if not hasattr(job_instance, attr_name):
            continue

        attr_value = getattr(job_instance, attr_name)
        print_debug(f"Checking {attr_name} against {expected_type}")
        print_debug(f"Value: {attr_value}")
        print_debug(f"Expected: {expected_type}")

        if attr_value is not None:
            pass

        # Handle special case for System objects
        if expected_type is System and attr_value is not None:
            # Check if the value is a System instance
            if not isinstance(attr_value, System):
                validation_report.add_error(
                    critical=True,
                    errormsg=[f"Job.{attr_name} has incorrect type"],
                    info=[
                        f"Expected {System.__name__}, got {type(attr_value).__name__}",
                        f"Value: {attr_value}",
                    ],
                )
                has_errors = True
            else:
                # Check the System instance's types
                if not check_system_types(module, attr_value, validation_report):
                    has_errors = True
            continue  # Skip standard type checking for System objects

        if str(expected_type).startswith("list[") and "Environment" in str(
            expected_type
        ):
            # check if got None that's ok
            if attr_value is None:
                continue

            # Check if it's a list
            if not isinstance(attr_value, list):
                validation_report.add_error(
                    critical=True,
                    errormsg=[f"Job.{attr_name} has incorrect type"],
                    info=[
                        f"Expected list of Environment objects, got {type(attr_value).__name__}",
                        f"Value: {attr_value}",
                    ],
                )
                has_errors = True
                continue

            # Check that all items are Environment instances (if it's a list)
            if attr_value and not all(
                isinstance(item, Environment) for item in attr_value
            ):
                validation_report.add_error(
                    critical=True,
                    errormsg=[f"Job.{attr_name} contains non-Environment objects"],
                    info=[
                        "All items in the list must be Environment objects",
                        f"Value: {attr_value}",
                    ],
                )
                has_errors = True
            continue

        if expected_type is Modules or str(expected_type) == "Modules":
            if not isinstance(attr_value, Modules):
                validation_report.add_error(
                    critical=True,
                    errormsg=[f"Job.{attr_name} has incorrect type"],
                    info=[
                        f"Expected Modules object, got {type(attr_value).__name__}",
                        f"Value: {attr_value}",
                    ],
                )
                has_errors = True
            continue

        # Handle the exec_comand list[str] case
        if str(expected_type).startswith("list[") and "str" in str(expected_type):
            # Check if it's a list
            if not isinstance(attr_value, list):

                # If Exec_command is a string, convert it to a list
                if isinstance(attr_value, str):
                    attr_value = [attr_value]
                else:
                    validation_report.add_error(
                        critical=True,
                        errormsg=[f"Job.{attr_name} has incorrect type"],
                        info=[
                            f"Expected list of strings, got {type(attr_value).__name__}",
                            f"Value: {attr_value}",
                        ],
                    )
                    has_errors = True
                    continue

            # Check that all items are strings (if it's a list)
            if attr_value and not all(isinstance(item, str) for item in attr_value):
                validation_report.add_error(
                    critical=True,
                    errormsg=[f"Job.{attr_name} contains non-string objects"],
                    info=[
                        "All items in the list must be strings",
                        f"Value: {attr_value}",
                    ],
                )
                has_errors = True
            continue

        # Standard type checking for other attributes
        if attr_value is not None:  # Only check non-None values
            # Handle union types (like int | None)
            if isinstance(expected_type, tuple):
                type_match = any(isinstance(attr_value, t) for t in expected_type)
            else:
                type_match = isinstance(attr_value, expected_type)

            if not type_match:
                validation_report.add_error(
                    critical=True,
                    errormsg=[f"Job.{attr_name} has incorrect type"],
                    info=[
                        f"Expected {_format_type_name(expected_type)}, got {type(attr_value).__name__}",
                        f"Value: {attr_value}",
                    ],
                )
                has_errors = True

    return not has_errors


def _format_type_name(type_obj):
    """Helper to format type names for error messages"""
    import types

    # Handle the newer Union syntax (int | str) from Python 3.10+
    if isinstance(type_obj, types.UnionType):
        # Get the args of the union type and format them
        return " or ".join([_format_type_name(arg) for arg in type_obj.__args__])

    # Handle tuples of types (older Union representation or custom combinations)
    if isinstance(type_obj, tuple):
        return " or ".join(t.__name__ for t in type_obj)

    # For simple types, just return the name
    return type_obj.__name__


def check_class_parameter_types(module, validation_report):
    """
    Check that the class parameters in the module have the correct types.

    Args:
        module: The loaded Python module containing class definitions
        validation_report: The validation report to add errors to

    Returns:
        bool: True if all parameters have correct types, False otherwise
    """
    has_errors = False

    # Find any Jobs instance in the module
    jobs_instance = None
    jobs_jobs = []

    for _, var_value in vars(module).items():
        if var_value.__class__.__name__ == "Jobs":
            jobs_instance = var_value
            break

    # If we found a Jobs instance, check its jobs
    if (
        jobs_instance
        and hasattr(jobs_instance, "get_jobs")
        and callable(jobs_instance.get_jobs)
    ):
        jobs_jobs = jobs_instance.get_jobs()
        print_debug(f"Jobs instance found: {jobs_instance}")

    if not jobs_jobs:
        validation_report.add_error_entry(
            missing_expected_types_ErrorMsg("Jobs instance")
        )
        print_error(
            "No Job found in the Jobs instance. Check that the Jobs instance is created correctly."
        )
        return False

    # Check each job
    for job in jobs_jobs:
        print_warning(f"Checking job: {job}")
        has_errors = not check_job_types(module, job, validation_report) or has_errors

    return not has_errors
