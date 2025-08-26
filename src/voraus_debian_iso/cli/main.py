"""Contains the main CLI entry point."""

import logging
from enum import Enum

import typer
from rich.logging import RichHandler

from voraus_debian_iso import get_app_name, get_app_version
from voraus_debian_iso.cli.build import _cli_build

_logger = logging.getLogger(__name__)


app = typer.Typer()
app.command(name="build", help="Builds the voraus debian ISO")(_cli_build)


class LogLevel(str, Enum):
    """Enum for log levels for typer."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


def print_version(do_print: bool) -> None:
    """Prints the version of the software.

    Args:
        do_print: If the version shall be printed.

    Raises:
        typer.Exit: After the version was printed.
    """
    if do_print:
        print(get_app_version())
        raise typer.Exit()


@app.callback()
def _common(
    _: bool = typer.Option(
        False,
        "--version",
        callback=print_version,
        is_eager=True,
        help="Print the installed version of the software.",
    ),
    log_level: LogLevel = typer.Option(LogLevel.INFO, help="The log level"),
) -> None:
    rich_handler = RichHandler()
    rich_handler.setFormatter(logging.Formatter("%(message)s"))
    logger = logging.getLogger()
    logger.handlers = [rich_handler]
    logger.setLevel(log_level.value)
    _logger.info(f"Starting {get_app_name()}@{get_app_version()}")


typer_click_object = typer.main.get_command(app)

if __name__ == "__main__":  # pragma: no cover
    app()
