"""Contains common CLI methods."""

import logging
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
