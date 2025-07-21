import importlib.util
from types import ModuleType

from utils.printers import print_debug, print_error, print_info, print_warning
from utils.slurmifyValidationReport import SlurmifyValidationReport
from errorMsgs.StructuralErrors import (
    exceptionMsg,
    importErrorMsg,
    missingJobMsg,
    missingJobsMsg,
    missingResourcesMsg,
    missingSystemMsg,
    nameErrorMsg,
    syntaxErrorMsg,
    unexpectedKeywordMsg,
    wrongJobsVariableNameMsg,
)
from utils.typeValidators import check_class_parameter_types


def check_class_validation(
    path: str, validation_report: SlurmifyValidationReport
) -> tuple[bool, ModuleType | None, SlurmifyValidationReport]:
    """Check if the class has the required attributes and methods"""

    print_info(f"Checking class validation for {path}")

    # Phase 1: Initial loading and syntax checking
    try:
        # Load the Config file as a module
        spec = importlib.util.spec_from_file_location("pythonSlurmConfig", path)
        if spec is None:
            validation_report.add_error(
                critical=True,
                errormsg=[f"Cannot load {path}"],
                info=["Check that the file exists and has proper permissions"],
            )
            return False, None, validation_report

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except SyntaxError as e:
        print_error(f"Syntax Error in {path}: {e}")
        validation_report.add_error_entry(syntaxErrorMsg(e))
        return False, None, validation_report
    except ImportError as e:
        print_error(f"Import Error in {path}: {e}")
        validation_report.add_error_entry(importErrorMsg(e))
        return False, None, validation_report
    except NameError as e:
        print_error(f"Name Error in {path}: {e}")
        validation_report.add_error_entry(nameErrorMsg(e))
        return False, None, validation_report
    except Exception as e:
        print_error(f"Unexpected Error in {path}: {e}")
        validation_report.add_error_entry(exceptionMsg(e))
        return False, None, validation_report

    return True, module, validation_report


def check_if_required_classes_exist(
    module: ModuleType, validation_report: SlurmifyValidationReport
) -> tuple[bool, ModuleType | None, SlurmifyValidationReport]:
    has_critical_error = False

    if not hasattr(module, "Jobs"):
        validation_report.add_error_entry(missingJobsMsg())
        has_critical_error = True

    if hasattr(module, "Jobs"):
        jobs_instances = []
        for var_name, var_value in vars(module).items():
            # print_debug(f"var_name: {var_name}, var_value: {var_value}")

            if var_value.__class__.__name__ == "Jobs":
                print_warning(
                    f"var_value.__class__.__name__ {var_value.__class__.__name__}"
                )
                jobs_instances.append(var_name)

        if not jobs_instances:
            validation_report.add_error_entry(missingJobsMsg())
            has_critical_error = True

        # If we have Jobs instances with different names
        if jobs_instances and not ("Jobs" in jobs_instances):
            print_debug(f"Jobs instances found with different names: {jobs_instances}")
            other_names = ", ".join([f"'{name}'" for name in jobs_instances])
            validation_report.add_error_entry(
                wrongJobsVariableNameMsg(names=other_names)
            )
            has_critical_error = True

    if not hasattr(module, "Job"):
        validation_report.add_error_entry(missingJobMsg())
        has_critical_error = True
        variable_name = getattr(module, "Job", None)

        print_error(
            f"Job variable name is not correct. Expected 'Job', got '{variable_name}'"
        )

    if not hasattr(module, "System"):
        validation_report.add_error_entry(missingSystemMsg())
        has_critical_error = True

    if not hasattr(module, "Resources"):
        validation_report.add_error_entry(missingResourcesMsg())
        has_critical_error = True

    return not has_critical_error, module, validation_report


def load_python_conf_file(
    path: str,
) -> tuple[ModuleType | None, SlurmifyValidationReport]:
    """Load Python config file and return module and validation report with any errors found

    Returns:
        tuple: (loaded module or None, validation report with all detected errors)
    """
    # Create validation report upfront to collect all errors
    validation_report = SlurmifyValidationReport("ConfigValidation")
    module = None
    has_critical_error = False

    class_validity, module, validation_report = check_class_validation(
        path, validation_report
    )

    if not class_validity:
        has_critical_error = True
        print_error(f"Class Validation Failed")
        return None, validation_report
    else:
        print_info(f"Class Validation Succefull")

    has_required_classes, module, validation_report = check_if_required_classes_exist(
        module, validation_report
    )

    if not has_required_classes:
        has_critical_error = True
        print_error(f"Failed Jobs requirements Check")
        # return None, validation_report
    else:
        print_info(f"Jobs requirements Check Succefull")

    # TODO: Check that the class parameters have the correct types for System Resources and Job
    # Check that the class parameters have the correct types
    if not has_critical_error:
        type_check_passed = check_class_parameter_types(module, validation_report)
        if not type_check_passed:
            print_error(f"Failed parameter type check")
            has_critical_error = True
        else:
            print_info(f"Parameter type check Successful")

    # Return module only if we didn't encounter any critical errors
    if has_critical_error:
        return None, validation_report
    return module, None
