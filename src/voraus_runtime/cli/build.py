"""This module defines the typer build method."""

import logging
from pathlib import Path
from typing import Annotated

import typer

from voraus_runtime.constants import DEFAULT_ARCHITECTURE, DEFAULT_DISTRO_NAME, DEFAULT_DISTRO_VERSION
from voraus_runtime.methods.cli.cli_build_methods import build_impl

_logger = logging.getLogger(__name__)


def _cli_build(
    distro_name: Annotated[
        str,
        typer.Option(help="The distro to use, e.g. 'debian'."),
    ] = DEFAULT_DISTRO_NAME,
    distro_version: Annotated[
        str,
        typer.Option(help="The distro base version to use."),
    ] = DEFAULT_DISTRO_VERSION,
    architecture: Annotated[
        str,
        typer.Option(help="The architecture to use."),
    ] = DEFAULT_ARCHITECTURE,
    output_directory: Annotated[Path, typer.Option(help="The output directory")] = Path("./output/"),
) -> None:  # noqa: disable=D103
    try:
        build_impl(
            distro_name=distro_name,
            distro_version=distro_version,
            architecture=architecture,
            output_directory=output_directory,
        )
    except KeyboardInterrupt as error:
        raise typer.Exit(0) from error
    except Exception as error:
        _logger.error(error)
        raise typer.Exit(1) from error
