"""Contains shell helper functions."""

from logging import getLogger
from subprocess import check_output

_logger = getLogger(__file__)


def execute_command(command: list[str]) -> None:
    """Executes a shell command and logs the command.

    Args:
        command: The command to execute as a list of strings.
    """
    _logger.debug(f"Executing command '{' '.join(command)}'")
    check_output(command)
