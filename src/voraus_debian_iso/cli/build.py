"""This module defines the typer build method."""

import logging
from pathlib import Path
from typing import Annotated

import typer

from voraus_debian_iso.constants import DEFAULT_ARCHITECTURE, DEFAULT_DEBIAN_VERSION
from voraus_debian_iso.methods.cli.cli_build_methods import build_impl

_logger = logging.getLogger(__name__)


def _cli_build(
    debian_version: Annotated[
        str,
        typer.Option(help="The debian base version to use."),
    ] = DEFAULT_DEBIAN_VERSION,
    architecture: Annotated[
        str,
        typer.Option(help="The architecture to use."),
    ] = DEFAULT_ARCHITECTURE,
    output_directory: Annotated[Path, typer.Option(help="The output directory")] = Path("./output/"),
) -> None:  # noqa: disable=D103
    try:
        build_impl(debian_version=debian_version, architecture=architecture, output_directory=output_directory)
    except KeyboardInterrupt as error:
        raise typer.Exit(0) from error
    except Exception as error:
        _logger.error(error)
        raise typer.Exit(1) from error
