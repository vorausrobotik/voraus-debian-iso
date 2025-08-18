"""Contains all constants."""

from pathlib import Path

from voraus_runtime import get_app_name

_PATH = Path(__file__).parent.resolve()

DATA_DIR = _PATH / "data"
DOCKERFILE_DIR = _PATH / "dockerfiles"
CACHE_DIR = Path("/tmp") / get_app_name() / "cache"
EXTRACTED_DIR = CACHE_DIR / "extracted"

DEFAULT_DEBIAN_VERSION = "13.0.0"
DEFAULT_ARCHITECTURE = "amd64"
ISO_FILENAME_TEMPLATE = "debian-{version}-{architecture}-netinst.iso"
DOWNLOAD_URL_TEMPLATE = "https://artifactory.vorausrobotik.com/artifactory/generic-local/debian-upstream/{file_name}"


MBR_FILE = CACHE_DIR / "isohdpfx.bin"
