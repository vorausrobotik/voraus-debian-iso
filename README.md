# voraus Debian ISO

[![CI](https://github.com/vorausrobotik/voraus-debian-iso/actions/workflows/pipeline.yml/badge.svg)](https://github.com/vorausrobotik/voraus-debian-iso/actions/workflows/pipeline.yml)
[![black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

This tool injects a preseed file into the official Debian netinst ISO,
enabling fully automated headless installations without user interaction.

<br />

# Installation

1) Download the latest ISO from our [Artifactory].
2) Create a bootable USB stick (e.g. with [Etcher], [Rufus] or via [command line]).
3) Plug in the USB stick into the IPC.
4) (Re)boot it and enter the boot menu (vendor specific, usually done by pressing
   <kbd>F2</kbd>, <kbd>F7</kbd>, <kbd>F12</kbd>, or <kbd>Del</kbd>).
5) Choose the USB stick as boot source.
6) Select `Automatic Headless Install` and press <kbd>⏎ Enter</kbd>. The installation process does not require any
   user interaction.
7) Once the installation has finished, the system will power off automatically.
8) Remove the USB stick and reboot the IPC.
9) You're all set! For additional configuration (e.g. realtime computation), please refer to our [IPC Ansible roles].

<br />

# Changelog

For the changelog, please refer to the [releases page].

<br />

# Documentation

For additional information, please refer to the [official documentation].

<br />


[Artifactory]: https://voraus.jfrog.io/artifactory/generic/voraus-debian-iso/
[Etcher]: https://github.com/balena-io/etcher
[Rufus]: https://rufus.ie/
[command line]: https://www.debian.org/releases/trixie/amd64/ch04s03.en.html
[releases page]: https://github.com/vorausrobotik/voraus-debian-iso/releases
[official documentation]: https://vorausrobotik.github.io/voraus-debian-iso/
[IPC Ansible roles]: https://github.com/vorausrobotik/voraus-ipc-tools-ansible/
