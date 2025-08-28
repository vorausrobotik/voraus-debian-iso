"""This module defines the typer start method."""

import logging

from voraus_debian_iso.methods.cli.cli_common_methods import try_call_impl
from voraus_debian_iso.methods.cli.cli_stop_methods import stop_impl

_logger = logging.getLogger(__name__)


def _cli_stop() -> None:  # noqa: disable=D103
    try_call_impl(function=stop_impl)
