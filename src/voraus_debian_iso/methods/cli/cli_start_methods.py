"""Contains all CLI start methods."""

import logging
import subprocess
import time
from pathlib import Path
from typing import Generator

from fabric import Connection
from paramiko.ssh_exception import NoValidConnectionsError, SSHException
from tenacity import after_log, retry, retry_if_exception_type
from tenacity.stop import stop_after_delay
from tenacity.wait import wait_fixed

from voraus_debian_iso.constants import QEMU_PID_FILE
from voraus_debian_iso.methods.cli.cli_common_methods import get_qemu_common_args

_logger = logging.getLogger(__name__)


def get_ssh_connection(username: str = "localuser") -> Generator[Connection, None, None]:
    """Establishes an SSH connection to the QEMU VM.

    Args:
        username: The username to use for the SSH connection.

    Yields:
        The SSH connection.
    """
    _logger.info("Establishing SSH connection to the QEMU VM...")
    with Connection(
        host="localhost",
        user=username,
        port=2222,
        connect_kwargs={"password": "voraus"},
        connect_timeout=60,
    ) as connection:
        retry(
            retry=retry_if_exception_type((NoValidConnectionsError, SSHException, TimeoutError)),
            wait=wait_fixed(2),
            stop=stop_after_delay(120),
            after=after_log(_logger, logging.DEBUG),
        )(connection.open)()
        yield connection


def start_impl(disk_file: Path, gui: bool = False) -> None:
    """CLI start implementation.

    Args:
        disk_file: The QEMU disk file to start.
        gui: Whether to start the VM with a GUI.

    Raises:
        FileNotFoundError: If the disk file doesn't exist.
    """
    if not disk_file.is_file():
        raise FileNotFoundError(f"Disk file {disk_file} doesn't exist.")

    if QEMU_PID_FILE.is_file():
        _logger.warning(f"QEMU VM is already running with PID file {QEMU_PID_FILE}. Stop it before starting again.")
        return

    _logger.info(f"Starting QEMU VM with disk file {disk_file}.")
    start_time = time.time()
    qemu_command = get_qemu_common_args() + [
        "-pidfile",
        str(QEMU_PID_FILE),
        "-drive",
        f"file={disk_file},format=qcow2",
        "-device",
        "e1000,netdev=eth0",
        "-netdev",
        "user,id=eth0,hostfwd=tcp::2222-:22",
        "-display",
        "gtk" if gui else "none",
        "-daemonize",
    ]

    with subprocess.Popen(args=qemu_command):
        try:
            next(get_ssh_connection())
        except StopIteration:
            pass
        _logger.info(f"QEMU VM started successfully after {time.time() - start_time} seconds.")
        return
