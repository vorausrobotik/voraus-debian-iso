"""This module defines the typer start method."""

import logging
from pathlib import Path
from typing import Annotated

import typer

from voraus_debian_iso.constants import DEFAULT_QEMU_DISK_FILE
from voraus_debian_iso.methods.cli.cli_common_methods import try_call_impl
from voraus_debian_iso.methods.cli.cli_start_methods import start_impl

_logger = logging.getLogger(__name__)


def _cli_start(
    disk_file: Annotated[
        Path,
        typer.Option(help="The QEMU disk file to start."),
    ] = DEFAULT_QEMU_DISK_FILE,
) -> None:  # noqa: disable=D103
    try_call_impl(function=start_impl, disk_file=disk_file)
