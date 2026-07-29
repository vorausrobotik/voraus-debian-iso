"""Contains all tests for the ISO."""

import sys

import pytest
from fabric import Connection

from voraus_debian_iso.methods.cli.cli_start_methods import get_ssh_connection


@pytest.mark.skipif(sys.platform != "linux", reason="Only supported on linux because it requires qemu")
class TestISO:
    """Contains all ISO tests."""

    # The packages of the installed system come from the Debian mirror and not from the ISO, so its point release
    # is whatever the mirror serves at installation time. Only the major release (trixie) is therefore asserted.
    def test_debian_version(self, dut: Connection) -> None:
        assert dut.run("cat /etc/debian_version").stdout.strip().startswith("13.")

    def test_debian_kernel(self, dut: Connection) -> None:
        kernel = dut.run("uname -r").stdout.strip()
        assert kernel.startswith("6.12.")
        assert kernel.endswith("+deb13-amd64")

    def test_python_version(self, dut: Connection) -> None:
        assert dut.run("python3 --version").stdout.strip().startswith("Python 3.13.")

    def test_root_ssh_access(self, dut: Connection) -> None:  # pylint: disable=unused-argument
        root_ssh_connection = next(get_ssh_connection(username="root"))
        assert root_ssh_connection.run("whoami").stdout.strip() == "root"

    def test_timezone(self, dut: Connection) -> None:
        assert dut.run("timedatectl show --property=Timezone --value").stdout.strip() == "Europe/Berlin"

    def test_sudo_available(self, dut: Connection) -> None:  # pylint: disable=unused-argument
        root_ssh_connection = next(get_ssh_connection(username="root"))
        assert root_ssh_connection.run("sudo --validate").ok
