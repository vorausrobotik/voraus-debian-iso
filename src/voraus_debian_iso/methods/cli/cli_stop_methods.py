"""Contains all CLI stop methods."""

import logging

from voraus_debian_iso.constants import QEMU_PID_FILE
from voraus_debian_iso.methods.shell import execute_command

_logger = logging.getLogger(__file__)


def stop_impl() -> None:
    """CLI stop implementation.

    Raises:
        Exception: If anything goes wrong.
    """
    if not QEMU_PID_FILE.is_file():
        _logger.warning(f"QEMU VM is not running. PID file {QEMU_PID_FILE} does not exist.")
        return

    try:
        pid = int(QEMU_PID_FILE.read_text().strip())
        _logger.info(f"Stopping QEMU VM with PID {pid}.")
        execute_command(["kill", str(pid)])
        QEMU_PID_FILE.unlink(missing_ok=True)
    except Exception as error:
        _logger.error(f"Failed to stop QEMU VM: {error}")
        raise
