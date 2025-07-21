from utils.slurmifyValidationReport import ErrorEntry


def missing_expected_types_ErrorMsg(className: str) -> ErrorEntry:
    return ErrorEntry(
        critical=True,
        msgFunctionName="missing_expected_types_ErrorMsg",
        errormsg=[f"Unable to get expected types for {className}"],
        info=[
            f"Check that the {className} class is defined correctly",
            "Expected types could not be determined",
        ],
    )


def wrong_attribute_msg(
    className: str,
    attrName: str,
) -> ErrorEntry:
    """
    Handle syntax errors in the configuration file.

    Args:
        error (SyntaxError): The syntax error to handle.

    Returns:
        ErrorEntry: An error entry with the details of the syntax error.
    """
    return ErrorEntry(
        critical=True,
        msgFunctionName="wrong_attribute_msg",
        errormsg=[f"Wrong attribute in configuration"],
        info=[
            "Check that the attribute is defined correctly",
            "Expected types could not be determined",
        ],
    )
