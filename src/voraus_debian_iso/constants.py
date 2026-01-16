"""Contains all constants."""

from pathlib import Path

from voraus_debian_iso import get_app_name

_PATH = Path(__file__).parent.resolve()

DATA_DIR = _PATH / "data"
DOCKERFILE_DIR = _PATH / "dockerfiles"
CACHE_DIR = Path("/tmp") / get_app_name() / "cache"
EXTRACTED_DIR = CACHE_DIR / "extracted"
DEFAULT_QEMU_DISK_FILE = CACHE_DIR / "qemu_disk.img"
QEMU_PID_FILE = CACHE_DIR / "qemu.pid"

DEFAULT_DEBIAN_VERSION = "13.3.0"
DEFAULT_ARCHITECTURE = "amd64"
ISO_FILENAME_TEMPLATE = "debian-{version}-{architecture}-netinst.iso"


MBR_FILE = CACHE_DIR / "isohdpfx.bin"
