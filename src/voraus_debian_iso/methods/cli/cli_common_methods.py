"""Contains common CLI methods."""

import logging
import os
from typing import Any, Callable

import typer

_logger = logging.getLogger(__name__)


def try_call_impl(function: Callable, *args: Any, **kwargs: Any) -> None:
    """Simple wrapper function that catches keyboard interrupts and other exceptions.

    Args:
        function: The function to call.
        args: The function args.
        kwargs: The function kwargs.

    Raises:
        typer.Exit: On keyboard interrupts or exceptions.
    """
    try:
        function(*args, **kwargs)
    except KeyboardInterrupt as error:
        raise typer.Exit(0) from error
    except Exception as error:
        _logger.error(error)
        raise typer.Exit(1) from error


def get_qemu_common_args() -> list[str]:
    """Get the common QEMU arguments.

    Returns:
        The common QEMU arguments with KVM support on non CI(GitHub Actions) environments.
    """
    args = [
        "qemu-system-x86_64",
        "-m",
        "2G",
    ]
    if os.environ.get("CI"):
        _logger.warning("Running in CI mode, disabling KVM. This will result in reduced performance.")
    else:
        args.append("-enable-kvm")
    return args
