"""This module defines the typer install method."""

import logging
from pathlib import Path
from typing import Annotated

import typer

from voraus_debian_iso.constants import DEFAULT_QEMU_DISK_FILE
from voraus_debian_iso.methods.cli.cli_common_methods import try_call_impl
from voraus_debian_iso.methods.cli.cli_install_methods import install_impl

_logger = logging.getLogger(__name__)


def _cli_install(
    iso_file: Annotated[
        Path,
        typer.Option(help="The ISO file to install."),
    ],
    disk_file: Annotated[
        Path,
        typer.Option(help="The QEMU disk file to create/use."),
    ] = DEFAULT_QEMU_DISK_FILE,
) -> None:  # noqa: disable=D103
    try_call_impl(function=install_impl, iso_file=iso_file, disk_file=disk_file)
