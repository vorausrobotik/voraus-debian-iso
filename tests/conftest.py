"""This module contains pytest fixtures."""

from __future__ import annotations

import logging
import os
import subprocess
import time
from pathlib import Path
from typing import Generator

import pexpect
import pytest
from fabric import Connection
from paramiko.ssh_exception import NoValidConnectionsError, SSHException
from tenacity import retry, retry_if_exception_type
from tenacity.stop import stop_after_delay
from tenacity.wait import wait_fixed

from voraus_runtime.constants import CACHE_DIR

_logger = logging.getLogger(__file__)


@pytest.fixture(scope="session", name="resource_dir")
def resource_dir_fixture() -> Path:
    """Returns the path to the test resource directory.

    Returns:
        Path: The resource directory path.
    """
    return Path(__file__).parent.joinpath("resources")


def _install_iso(iso_path: Path, qemu_command: list[str]) -> None:
    _logger.info(f"Installing ISO {iso_path} on QEMU VM. This may take a while...")
    start_time = time.time()
    install_process = pexpect.spawn(
        " ".join(qemu_command + ["-boot", "d", "-cdrom", str(iso_path)]),
        timeout=30000,
    )
    install_process.expect("Booting from DVD/CD", timeout=1)
    time.sleep(5)  # Make sure GRUB is ready...
    install_process.sendline("")  #  Select headless install (Press enter)
    while True:
        try:
            install_process.expect("\r\n", timeout=1)
        except pexpect.TIMEOUT:
            continue  # No output for 1 second, just continue
        except pexpect.EOF:
            break  # End of output -> Installation has finished
    _logger.info(f"Installation finished after {time.time() - start_time} seconds")


@pytest.fixture(scope="session", name="dut")
def device_under_test_fixture() -> Generator[Connection, None, None]:
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

    qemu_image_path = Path(CACHE_DIR) / "test" / "qemu_image.qcow2"
    qemu_command = [
        "qemu-system-x86_64",
        "-enable-kvm",
        "-m",
        "2G",
        "-drive",
        f"file={qemu_image_path},format=qcow2",
        "-device",
        "e1000,netdev=eth0",
        "-netdev",
        "user,id=eth0,hostfwd=tcp::2222-:22",
        "-nographic",
        "-serial",
        "mon:stdio",
    ]
    if not qemu_image_path.is_file():
        qemu_image_path.parent.mkdir(exist_ok=True, parents=True)
        subprocess.check_call(["qemu-img", "create", "-f", "qcow2", str(qemu_image_path), "5G"])
        _install_iso(iso_path=iso_path, qemu_command=qemu_command)

    logging.getLogger("paramiko").setLevel(logging.WARNING)
    with subprocess.Popen(args=qemu_command) as qemu_process:
        with Connection(
            host="localhost",
            user="localuser",
            port=2222,
            connect_kwargs={"password": "voraus"},
            connect_timeout=60,
        ) as connection:
            retry(
                retry=retry_if_exception_type((NoValidConnectionsError, SSHException, TimeoutError)),
                wait=wait_fixed(2),
                stop=stop_after_delay(60),
            )(connection.open)()
            yield connection
        qemu_process.terminate()
        qemu_process.wait(timeout=5)
        if qemu_process.returncode is None:
            qemu_process.kill()
