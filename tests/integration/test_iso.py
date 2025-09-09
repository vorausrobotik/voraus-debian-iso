"""Contains all tests for the ISO."""

import sys

import pytest
from fabric import Connection


@pytest.mark.skipif(sys.platform != "linux", reason="Only supported on linux because it requires qemu")
class TestISO:
    """Contains all ISO tests."""

    def test_debian_version(self, dut: Connection) -> None:
        assert dut.run("cat /etc/debian_version").stdout.strip() == "13.1"

    def test_debian_kernel(self, dut: Connection) -> None:
        assert dut.run("uname -r").stdout.strip() == "6.12.43+deb13-amd64"

    def test_python_version(self, dut: Connection) -> None:
        assert dut.run("python3 --version").stdout.strip() == "Python 3.13.5"
