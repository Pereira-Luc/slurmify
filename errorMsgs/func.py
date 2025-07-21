from utils.config_info import (
    Job,
    Environment,
    System,
    Jobs,
    Resources,
    Logs,
    Modules,
    Module,
)
import inspect
from typing import Union, get_args, get_origin, get_type_hints


# TODO: This class is not entirely correct it takes the classes that are imported in this file not config_info.py
def get_class_from_name(class_name: str):
    """
    Get a class from its name in the current module.

    Args:
        class_name (str): The name of the class to retrieve.

    Returns:
        type: The class object if found, None otherwise.
    """
    # Get the current module
    current_module = inspect.getmodule(inspect.currentframe())

    # Check if the class exists in the current module
    if hasattr(current_module, class_name):
        return getattr(current_module, class_name)
    else:
        return None


def get_all_valid_classes():
    """
    Get all valid classes from the current module.

    Returns:
        list: A list of class objects.
    """
    # Get the current module
    current_module = inspect.getmodule(inspect.currentframe())

    # Get all class names in the current module
    classes = [
        name for name, obj in inspect.getmembers(current_module) if inspect.isclass(obj)
    ]

    return classes


def get_expected_types(cls):
    """
    Extract expected types from a class's __init__ method and variable annotations.
    Returns a dictionary mapping attribute names to their expected types,
    suitable for direct use in type validation.

    Args:
        cls: The class to extract type information from

    Returns:
        dict: Mapping of attribute names to their expected types
    """
    expected_types = {}

    # Try to get types from __init__ parameters
    try:
        hints = get_type_hints(cls.__init__)

        # Remove 'self' and 'return' entries
        hints.pop("self", None)
        hints.pop("return", None)

        # Process each type hint
        for param_name, type_hint in hints.items():
            # Convert Union[X, None] or Optional[X] to tuple (X, type(None))
            if get_origin(type_hint) is Union:
                args = get_args(type_hint)
                if type(None) in args:
                    # This is a Union with None (Optional)
                    other_types = tuple(arg for arg in args if arg is not type(None))
                    if len(other_types) == 1:
                        # Common case: Union[X, None] -> (X, type(None))
                        expected_types[param_name] = (other_types[0], type(None))
                    else:
                        # More complex case: Union[X, Y, None] -> (X, Y, type(None))
                        expected_types[param_name] = tuple(args)
                else:
                    # This is a Union without None
                    expected_types[param_name] = tuple(args)
            else:
                # Regular type
                expected_types[param_name] = type_hint
    except Exception:
        # If __init__ type hints fail, try to get them from variable annotations
        print(
            f"Failed to get type hints from __init__ for {cls.__name__}, trying variable annotations"
        )

    return expected_types


def get_class_type_hints(
    classes: list = [Resources, Environment, Job, System, Logs, Module, Modules, Jobs],
    class_name: str = None,
) -> list:
    """Extract type information from Slurmify classes dynamically."""
    if classes is None or len(classes) == 0:
        classes = [Resources, Environment, Job, System, Logs, Module, Modules, Jobs]

    type_info = []

    for cls in classes:

        class_name = cls.__name__
        type_info.append(f"{class_name} parameters:")

        # Safty checks so that when new classes are added we don't break the code
        try:
            # Try to get __init__ method
            init_method = cls.__init__

            # Get type hints
            try:
                hints = get_type_hints(init_method)

                # Remove 'return' and 'self' entries
                if "return" in hints:
                    del hints["return"]
                if "self" in hints:
                    del hints["self"]

                # Get default values from signature
                sig = inspect.signature(init_method)
                params = sig.parameters

                # If no type hints found, we'll try to at least show parameters
                if not hints and len(params) > 1:  # More than just 'self'
                    type_info.append(
                        f"  (Parameters available but no type annotations found)"
                    )
                    for param_name, param in params.items():
                        if param_name != "self":
                            default_str = ""
                            if param.default != inspect.Parameter.empty:
                                default = param.default
                                if default is None:
                                    default_str = " (default: None)"
                                elif isinstance(default, str):
                                    default_str = f" (default: '{default}')"
                                else:
                                    default_str = f" (default: {default})"
                            type_info.append(
                                f"  - {class_name}.{param_name}{default_str}"
                            )
                    type_info.append("")
                    continue

                for param_name, type_hint in hints.items():
                    # Check if parameter has default value
                    default_str = ""
                    if (
                        param_name in params
                        and params[param_name].default != inspect.Parameter.empty
                    ):
                        default = params[param_name].default
                        if default is None:
                            default_str = " (default: None)"
                        elif isinstance(default, str):
                            default_str = f" (default: '{default}')"
                        else:
                            default_str = f" (default: {default})"

                    # Format the type hint to there common name
                    type_name = str(type_hint).replace("typing.", "")
                    type_name = type_name.replace("NoneType", "None")
                    type_name = type_name.replace(" | ", " or ")

                    type_info.append(
                        f"  - {class_name}.{param_name}: {type_name}{default_str}"
                    )
            except Exception as e:
                type_info.append(f"  (Could not extract type hints: {str(e)})")

                # Try to at least show parameters from signature
                try:
                    sig = inspect.signature(init_method)
                    params = sig.parameters
                    for param_name, param in params.items():
                        if param_name != "self":
                            default_str = ""
                            if param.default != inspect.Parameter.empty:
                                default = param.default
                                if default is None:
                                    default_str = " (default: None)"
                                elif isinstance(default, str):
                                    default_str = f" (default: '{default}')"
                                else:
                                    default_str = f" (default: {default})"
                            type_info.append(
                                f"  - {class_name}.{param_name}{default_str}"
                            )
                except Exception:
                    type_info.append("  (Could not extract parameters)")

            type_info.append("")
        except Exception as e:
            type_info.append(f"  (Error accessing class: {str(e)})")
            type_info.append("")

    return type_info
