"""Contains all CLI install methods."""

import logging
import time
from pathlib import Path

import pexpect

from voraus_debian_iso.constants import QEMU_COMMON_ARGS
from voraus_debian_iso.methods.shell import execute_command

_logger = logging.getLogger(__name__)


def install_impl(iso_file: Path, disk_file: Path) -> None:
    """CLI install implementation.

    Args:
        iso_file: The ISO to use for installation.
        disk_file: The QEMU disk file to create/use.
    """
    if disk_file.is_file():
        _logger.warning(f"Disk file {disk_file} already exists. It will be overwritten.")
        disk_file.unlink()

    disk_file.parent.mkdir(parents=True, exist_ok=True)
    _logger.info(f"Creating disk file {disk_file}...")
    execute_command(["qemu-img", "create", "-f", "qcow2", str(disk_file), "5G"])

    qemu_command = QEMU_COMMON_ARGS + [
        "-drive",
        f"file={disk_file},format=qcow2",
        "-nographic",
        "-serial",
        "mon:stdio",
        "-boot",
        "d",
        "-cdrom",
        str(iso_file),
    ]

    start_time = time.time()
    install_process = pexpect.spawn(" ".join(qemu_command), timeout=30000)
    _logger.info("Waiting for GRUB to be ready...")
    install_process.expect("Booting from DVD/CD", timeout=10)
    _logger.info(f"Installing ISO {iso_file} in a QEMU VM. This may take a while...")
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
