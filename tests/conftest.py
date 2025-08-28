"""This module contains pytest fixtures."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Generator

import pytest
from fabric import Connection
from typer.testing import CliRunner

from voraus_debian_iso.cli.main import app
from voraus_debian_iso.constants import DEFAULT_QEMU_DISK_FILE
from voraus_debian_iso.methods.cli.cli_start_methods import get_ssh_connection

_logger = logging.getLogger(__file__)


@pytest.fixture(scope="session", name="resource_dir")
def resource_dir_fixture() -> Path:
    """Returns the path to the test resource directory.

    Returns:
        Path: The resource directory path.
    """
    return Path(__file__).parent.joinpath("resources")


@pytest.fixture(scope="session", name="cli_runner")
def cli_runner_fixture() -> CliRunner:
    """Returns a typer/click CliRunner with increased terminal width.

    Returns:
        The CliRunner object for testing the CLI.
    """
    return CliRunner(env={"COLUMNS": "120"})


@pytest.fixture(scope="session", name="dut")
def device_under_test_fixture(cli_runner: CliRunner) -> Generator[Connection, None, None]:
    images_path = Path(__file__).parent.parent / "output"
    iso_files = list(images_path.glob("*.iso"))
    match len(iso_files):
        case 0:
            raise RuntimeError(f"No ISO file found in {images_path}")
        case 1:
            iso_path = images_path / iso_files[0]
        case _:
            iso_path = max(iso_files, key=os.path.getctime)
            _logger.warning(f"Multiple ISO files found in {images_path}: {iso_files}. Using latest ISO file {iso_path}")

    if not DEFAULT_QEMU_DISK_FILE.is_file():
        cli_runner.invoke(app, ["install", "--iso-file", str(iso_path), "--disk-file", str(DEFAULT_QEMU_DISK_FILE)])

    cli_runner.invoke(app, ["start", "--disk-file", str(DEFAULT_QEMU_DISK_FILE)])

    yield from get_ssh_connection()

    cli_runner.invoke(app, ["stop"])
