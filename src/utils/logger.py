__author__ = "Adnan Karol"
__version__ = "1.0.0"
__maintainer__ = "Adnan Karol"
__email__ = "adnanmushtaq5@gmail.com"
__status__ = "DEV"

# Import Dependencies
import sys
from datetime import datetime

# ANSI escape codes for colors
RESET = "\033[0m"
COLORS = {
    "INFO": "\033[94m",  # Blue
    "SUCCESS": "\033[92m",  # Green
    "WARN": "\033[93m",  # Yellow
    "ERROR": "\033[91m",  # Red
    "DEBUG": "\033[90m",  # Gray
}


def log_info(message: str) -> None:
    """
    Logs an informational message to stdout.

    Args:
        message (str): The message to log.

    Returns:
        None
    """
    print(f"{COLORS['INFO']}[INFO] {message}{RESET}", file=sys.stdout)


def log_success(message: str) -> None:
    """
    Logs a success message to stdout.

    Args:
        message (str): The message to log.

    Returns:
        None
    """
    print(f"{COLORS['SUCCESS']}[SUCCESS] {message}{RESET}", file=sys.stdout)


def log_warn(msg: str) -> None:
    """
    Logs a warning message to stdout.

    Args:
        msg (str): The warning message to log.

    Returns:
        None
    """
    print(
        f"{COLORS['WARN']}[WARN] {datetime.now().strftime('%H:%M:%S')}:{RESET} {msg}",
        file=sys.stdout,
    )


def log_error(msg: str) -> None:
    """
    Logs an error message to stderr.

    Args:
        msg (str): The error message to log.

    Returns:
        None
    """
    print(
        f"{COLORS['ERROR']}[ERROR] {datetime.now().strftime('%H:%M:%S')}:{RESET} {msg}",
        file=sys.stderr,
    )


def log_debug(msg: str) -> None:
    """
    Logs a debug message to stdout.

    Args:
        msg (str): The debug message to log.

    Returns:
        None
    """
    print(
        f"{COLORS['DEBUG']}[DEBUG] {datetime.now().strftime('%H:%M:%S')}:{RESET} {msg}",
        file=sys.stdout,
    )
