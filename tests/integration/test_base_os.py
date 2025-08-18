"""Contains all tests for the unmodified base OS before applying any changes via ansible."""

from fabric import Connection


def test_debian_version(dut: Connection) -> None:
    assert dut.run("cat /etc/debian_version").stdout.strip() == "13.0"


def test_debian_versionsecond(dut: Connection) -> None:
    assert dut.run("uname -r").stdout.strip() == "6.12.41+deb13-amd64"
