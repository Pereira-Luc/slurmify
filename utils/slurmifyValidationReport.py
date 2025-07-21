from utils.config_info import Job

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
RESET = "\033[0m"


"""This class will be used to handle the respins of the Slurmify validation

Attributes:
    job_name (str): The name of the job
    valid (bool): True if the job is valid, False otherwise
    errors list[(criticale:bool, errormsg:list[str] ,warning:list[str], info:list[str])]: A list of errors that describe the validation results
    messages (list[str]): A list of messages that describe the validation results
"""

"""How the structure should look

    {
        job_name: "TestJob",
        valid: True,
        
        errors: [
            {
                critical: False,  # If the error is critical the job will not be valid but it can still have additional infos
                errormsg: [CPU count is Negative],
                warning: [CPU count was set to 0],
                info: [
                "To fix this error do this ..."
                ]
            }
        ],
    }
"""


class ErrorEntry:
    """Class to represent an error entry in the validation report.

    Attributes:
        critical (bool): Indicates if the error is critical.
        errormsg (list[str]): List of error messages.
        warning (list[str]): List of warnings.
        info (list[str]): List of informational messages.
        msgFunctionName (str): Name of the function that created the error message. (DEBUG)
    """

    def __init__(
        self, errormsg, critical=False, warning=None, info=None, msgFunctionName=None
    ):
        """Initialize an ErrorEntry instance.

        Args:
            critical (bool, optional): If True, marks the error as critical. Defaults to False.
            errormsg (list[str], optional): List of error messages. Defaults to None.
            warning (list[str], optional): List of warnings. Defaults to None.
            info (list[str], optional): List of informational messages. Defaults to None.
        """
        self.msgFunctionName = msgFunctionName
        self.critical = critical
        self.errormsg = errormsg
        self.warning = warning or []
        self.info = info


class SlurmifyValidationReport:
    """Class to handle responses from Slurmify validation.

    This class provides a structured way to manage validation results for Slurm jobs,
    including tracking validity, errors, warnings, and informational messages.
    """

    def __init__(self, job_name, job: Job = None):
        """Initialize a JobResponseHandler instance.

        Args:
            job_name (str): The name of the job being validated.
        """
        self.job: Job | None = job  # Store the Job instance for later use
        self.job_name = job_name
        self.valid = True  # By default, assume job is valid
        self.errors: list[ErrorEntry] = []  # List to hold error entries
        self.messages = []

    def add_error(self, critical=False, errormsg=None, warning=None, info=None):
        """Add an error entry to the response.

        Args:
            critical (bool, optional): If True, marks the job as invalid. Defaults to False.
            errormsg (list[str], optional): List of error messages. Defaults to None.
            warning (list[str], optional): List of warnings. Defaults to None.
            info (list[str], optional): List of informational messages. Defaults to None.
        """
        if critical:
            self.valid = False

        error_entry = ErrorEntry(
            errormsg=errormsg or [],  # errormsg is a required positional argument
            critical=critical,
            warning=warning or [],
            info=info or [],
        )

        self.errors.append(error_entry)

    def add_error_entry(self, error_entry: ErrorEntry):
        """Add an ErrorEntry instance to the response.

        Args:
            error_entry (ErrorEntry): An instance of ErrorEntry to add.
        """
        if error_entry.critical:
            self.valid = False

        self.errors.append(error_entry)

    def add_message(self, message):
        """Add a general message to the response.

        Args:
            message (str): Message to add.
        """
        self.messages.append(message)

    def mark_invalid(self):
        """Mark the job as invalid without adding an error."""
        self.valid = False

    def has_critical_errors(self):
        """Check if the job has any critical errors.

        Returns:
            bool: True if there are any critical errors, False otherwise.
        """
        return any(error["critical"] for error in self.errors)

    def get_critical_errors(self):
        """Get a list of all critical errors.

        Returns:
            list: List of all critical errors.
        """
        return [error for error in self.errors if error.critical]

    def count_issues(self):
        """Count the number of errors, warnings, and info messages.

        Returns:
            dict: Dictionary with counts for each type of message.
        """

        error_count = sum(len(error.errormsg) for error in self.errors)
        warning_count = sum(len(error.warning) for error in self.errors)
        info_count = sum(len(error.info) for error in self.errors)

        return {
            "errors": error_count,
            "warnings": warning_count,
            "info": info_count,
            "total": error_count + warning_count + info_count,
        }

    def has_issues(self):
        """Check if the job has any errors, warnings, or informational messages.

        Returns:
            bool: True if there are any issues, False otherwise.
        """
        return len(self.errors) > 0

    def merge(self, other_handler):
        """Merge another JobResponseHandler into this one.

        Args:
            other_handler (JobResponseHandler): Another handler to merge with this one.

        Returns:
            JobResponseHandler: Self, with the merged data.
        """
        if not self.valid or not other_handler.valid:
            self.valid = False

        self.errors.extend(other_handler.errors)
        self.messages.extend(other_handler.messages)

        return self

    def get_name(self):
        return self.job_name

    def __str__(self):
        """Generate a string representation of the job response with color formatting.

        Returns:
            str: Formatted string showing job validation results with colors for CLI.
        """
        # Job name and validation status with color

        result = f"{BLUE}{BOLD}============================================================================{RESET}"
        result += f"\nJob '{BOLD}{self.job_name}{RESET}' validation report:\n"
        result += f"{BLUE}{BOLD}============================================================================{RESET}\n"

        if self.valid:
            result += f"Job '{BOLD}{self.job_name}{RESET}': {GREEN}{BOLD}Valid{RESET}\n"
        else:
            result += f"Job '{BOLD}{self.job_name}{RESET}': {RED}{BOLD}Invalid{RESET}\n"

        counts = self.count_issues()

        # Color-coded summary counts
        result += f"Validation summary: "
        result += f"{RED}{counts['errors']} errors{RESET}, "
        result += f"{YELLOW}{counts['warnings']} warnings{RESET}, "
        result += f"{CYAN}{counts['info']} information messages{RESET}\n"

        # Critical errors count with color
        critical_count = len(self.get_critical_errors())
        if critical_count > 0:
            result += f"This slurmify script has {RED}{BOLD}{critical_count} critical errors{RESET}\n"
        else:
            result += f"This slurmify script has {GREEN}0 critical errors{RESET}\n"

        if self.errors:
            result += f"{BOLD}Validation Errors{RESET}\n"

            for i, error in enumerate(self.errors, 1):
                if hasattr(error, "msgFunctionName") and error.msgFunctionName:
                    result += f"  Error message provided by Function: {CYAN}{error.msgFunctionName}{RESET}\n"

                # Color-coded severity
                if error.critical:
                    severity = f"{RED}{BOLD}CRITICAL{RESET}"
                else:
                    severity = f"{YELLOW}WARNING{RESET}"

                result += f"  {BOLD}Issue {i}{RESET} ({severity}):\n"

                if error.errormsg:
                    result += f"    {BOLD}Errors:{RESET}\n"
                    for msg in error.errormsg:
                        result += f"      - {RED}{msg}{RESET}\n"

                if error.warning:
                    result += f"    {BOLD}Warnings:{RESET}\n"
                    for msg in error.warning:
                        result += f"      - {YELLOW}{msg}{RESET}\n"

                if error.info:
                    result += f"    {BOLD}Info:{RESET}\n"
                    for msg in error.info:
                        result += f"      - {CYAN}{msg}{RESET}\n"

        if self.messages:
            result += f"{BOLD}Additional messages:{RESET}\n"
            for msg in self.messages:
                result += f"  - {msg}\n"

        result += f"{BLUE}{BOLD}============================================================================{RESET}"
        result += f"\n"

        return result

    def for_llm(self):
        """Generate a formatted prompt for an LLM containing all validation information.

        Returns:
            str: A comprehensive prompt with validation details and fix instructions.
        """
        prompt = "# Slurmify Job Validation Report\n\n"

        # Job status
        prompt += f"Job '{self.job_name}' validation status: **{'VALID' if self.valid else 'INVALID'}**\n\n"

        # Issue counts
        counts = self.count_issues()
        prompt += f"Issue summary: {counts['errors']} errors, {counts['warnings']} warnings, {counts['info']} information messages\n"
        prompt += f"Critical errors: {len(self.get_critical_errors())}\n\n"

        # List all issues
        if self.errors:
            prompt += "## Validation Issues\n\n"
            for i, error in enumerate(self.errors, 1):
                severity = "CRITICAL" if error.critical else "WARNING"
                prompt += f"### Issue {i} ({severity})\n\n"

                if error.errormsg:
                    prompt += "#### Errors\n"
                    for msg in error.errormsg:
                        prompt += f"- {msg}\n"
                    prompt += "\n"

                if error.warning:
                    prompt += "#### Warnings\n"
                    for msg in error.warning:
                        prompt += f"- {msg}\n"
                    prompt += "\n"

                if error.info:
                    prompt += "#### How to Fix\n"
                    for msg in error.info:
                        prompt += f"- {msg}\n"
                    prompt += "\n"

        # Additional messages
        if self.messages:
            prompt += "## Additional Information\n\n"
            for msg in self.messages:
                prompt += f"- {msg}\n"

        # Add a final request for help
        prompt += "\n## Request\n"
        if not self.valid:
            prompt += "Please help fix the critical issues in this Slurmify job configuration. Check the doumentation about the classes an try again\n"
        else:
            prompt += "Please review this Slurmify job configuration for any potential improvements.\n"

        return prompt

    def for_llm_json_safe(self):
        """Generate a formatted prompt for an LLM containing all validation information.
        Ensures the output is safe for JSON transmission.

        Returns:
            str: A comprehensive prompt with validation details and fix instructions.
        """
        import json

        # Build the content in a structured way first
        content = {
            "title": "Slurmify Job Validation Report",
            "job_name": self.job_name,
            "validation_status": "VALID" if self.valid else "INVALID",
            "counts": self.count_issues(),
            "critical_errors": len(self.get_critical_errors()),
            "issues": [],
            "messages": self.messages,
            "request": (
                "Please review this Slurmify job configuration for any potential improvements."
                if self.valid
                else "Please help fix the critical issues in this Slurmify job configuration. Check the documentation about the classes and try again."
            ),
        }

        # Add issues in a structured way
        if self.errors:
            for i, error in enumerate(self.errors, 1):
                issue = {
                    "number": i,
                    "severity": "CRITICAL" if error.critical else "WARNING",
                    "errors": error.errormsg,
                    "warnings": error.warning,
                    "info": error.info,
                }
                content["issues"].append(issue)

        # Convert to JSON and back to ensure all special characters are properly escaped
        json_safe_content = json.loads(json.dumps(content))

        return json.dumps(json_safe_content, indent=2)
