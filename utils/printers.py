import utils.colors as COLOR_MAP

# Initialize the global variable
enable_print = False  # Default to no printing


def enable_printing(enable=True) -> None:
    """Enable printing for debugging"""
    global enable_print
    enable_print = enable


def print_error(error: str, debug: bool = enable_print) -> None:
    """Print error message in bold red color"""

    if debug or enable_print:
        print(f"{COLOR_MAP.RED} [ERROR] {error}{COLOR_MAP.RESET}")


def print_warning(warning: str, debug: bool = enable_print) -> None:
    """Print warning message in bold yellow color"""

    if debug or enable_print:
        print(f"{COLOR_MAP.YELLOW} [WARNING] {warning}{COLOR_MAP.RESET}")


def print_info(info: str, debug: bool = enable_print) -> None:
    """Print info message in bold green color"""

    if debug or enable_print:
        print(f"{COLOR_MAP.BLUE} [INFO] {info}{COLOR_MAP.RESET}")


def print_success(success: str, debug: bool = enable_print) -> None:
    """Print success message in bold blue color"""

    if debug or enable_print:
        print(f"{COLOR_MAP.GREEN} [SUCCESS] {success} {COLOR_MAP.RESET}")


def print_debug(debugStr: str, debug: bool = enable_print) -> None:
    """Print debug message in bold purple color"""

    if debug or enable_print:
        print(f"{COLOR_MAP.MAGENTA} [DEBUG] {debugStr}{COLOR_MAP.RESET}")
