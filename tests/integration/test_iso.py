"""Contains all tests for the ISO."""

import sys
from pathlib import Path

import pytest
from fabric import Connection

from voraus_debian_iso.methods.cli.cli_start_methods import get_ssh_connection


def get_physical_nics(dut: Connection) -> list[str]:
    """Returns the names of all physical NICs of the DUT.

    Virtual devices (like the loopback device) are excluded because they do not provide a device symlink in sysfs.

    Args:
        dut: The connection to the device under test.

    Returns:
        The NIC names, for example ["enp0s3"].
    """
    result = dut.run("find /sys/class/net -mindepth 1 -maxdepth 1 -exec test -e {}/device ';' -print")
    return [Path(path).name for path in result.stdout.split()]


@pytest.mark.skipif(sys.platform != "linux", reason="Only supported on linux because it requires qemu")
class TestISO:
    """Contains all ISO tests."""

    def test_debian_version(self, dut: Connection) -> None:
        assert dut.run("cat /etc/debian_version").stdout.strip() == "13.6"

    def test_debian_kernel(self, dut: Connection) -> None:
        assert dut.run("uname -r").stdout.strip() == "6.12.94+deb13-amd64"

    def test_python_version(self, dut: Connection) -> None:
        assert dut.run("python3 --version").stdout.strip() == "Python 3.13.5"

    def test_root_ssh_access(self, dut: Connection) -> None:  # pylint: disable=unused-argument
        root_ssh_connection = next(get_ssh_connection(username="root"))
        assert root_ssh_connection.run("whoami").stdout.strip() == "root"

    def test_timezone(self, dut: Connection) -> None:
        assert dut.run("timedatectl show --property=Timezone --value").stdout.strip() == "Europe/Berlin"

    def test_sudo_available(self, dut: Connection) -> None:  # pylint: disable=unused-argument
        root_ssh_connection = next(get_ssh_connection(username="root"))
        assert root_ssh_connection.run("sudo --validate").ok

    def test_networking_service_active(self, dut: Connection) -> None:
        # A duplicate interface stanza (for example because the interface used during the installation is configured
        # in /etc/network/interfaces as well as in /etc/network/interfaces.d) makes ifupdown fail.
        assert dut.run("systemctl is-active networking", warn=True).stdout.strip() == "active"

    def test_interfaces_file_only_configures_loopback(self, dut: Connection) -> None:
        interfaces = dut.run("cat /etc/network/interfaces").stdout
        stanzas = [line for line in interfaces.splitlines() if line.startswith("iface")]
        assert stanzas == ["iface lo inet loopback"]

    def test_all_nics_configured_for_dhcp(self, dut: Connection) -> None:
        nics = get_physical_nics(dut)
        assert nics, "The device under test does not provide any physical NIC"
        for nic in nics:
            stanza = dut.run(f"cat /etc/network/interfaces.d/{nic}").stdout
            assert f"allow-hotplug {nic}" in stanza
            assert f"iface {nic} inet dhcp" in stanza
            assert "inet " in dut.run(f"ip -4 address show {nic}").stdout
