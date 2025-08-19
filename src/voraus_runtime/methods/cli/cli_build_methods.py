"""Contains all CLI build methods."""

import hashlib
from logging import getLogger
from pathlib import Path
from shutil import copytree, rmtree
from urllib.request import urlretrieve

from setuptools_scm import get_version

from voraus_runtime.constants import (
    CACHE_DIR,
    DATA_DIR,
    DOWNLOAD_URL_TEMPLATE,
    EXTRACTED_DIR,
    ISO_FILENAME_TEMPLATE,
    MBR_FILE,
)
from voraus_runtime.methods.shell import execute_command

_logger = getLogger(__file__)


def build_impl(distro_name: str, distro_version: str, architecture: str, output_directory: Path) -> None:
    """CLI build implementation.

    Args:
        distro_name: The name of the distribution (e.g., "debian").
        distro_version: The distro version to use.
        architecture: The architecture to use.
        output_directory: The directory where the output ISO file will be saved.
    """
    CACHE_DIR.mkdir(exist_ok=True, parents=True)
    iso_path = _download_iso(architecture=architecture, version=distro_version)
    _extract_iso(iso_path=iso_path, extracted_dir=EXTRACTED_DIR)
    _patch_extracted_iso(extracted_iso_dir=EXTRACTED_DIR)
    _repack_iso(
        distro_name=distro_name,
        distro_version=distro_version,
        architecture=architecture,
        extracted_iso_dir=EXTRACTED_DIR,
        output_directory=output_directory,
    )


def _download_iso(architecture: str, version: str) -> Path:
    file_name = ISO_FILENAME_TEMPLATE.format(architecture=architecture, version=version)
    file_path = CACHE_DIR / file_name
    if file_path.is_file():
        _logger.info(f"{file_path} exists, skipping download")
    else:
        download_url = DOWNLOAD_URL_TEMPLATE.format(architecture=architecture, file_name=file_name)
        _logger.info(f"Downloading {download_url} to file {file_path}")
        urlretrieve(download_url, file_path)
    return file_path


def _extract_iso(iso_path: Path, extracted_dir: Path) -> None:
    if extracted_dir.is_dir():
        rmtree(extracted_dir)
    extracted_dir.mkdir()
    _logger.info(f"Extracting ISO {iso_path} to {extracted_dir}")
    execute_command(["bsdtar", "-C", str(extracted_dir), "-xf", str(iso_path)])
    execute_command(["chmod", "-R", "+rw", str(extracted_dir)])
    _logger.info(f"Generating file {MBR_FILE}")
    execute_command(["dd", f"if={iso_path}", "bs=1", "count=432", f"of={MBR_FILE}"])


def _patch_extracted_iso(extracted_iso_dir: Path) -> None:
    _configure_preseed(extracted_iso_dir=extracted_iso_dir)


def _configure_preseed(extracted_iso_dir: Path) -> None:
    _logger.info("Configuring preseed")
    preseed_dir = DATA_DIR / "preseed"
    preseed_file = preseed_dir / "preseed.cfg"
    preseed_checksum = hashlib.md5(preseed_file.read_bytes()).hexdigest()
    copytree(preseed_dir, extracted_iso_dir, dirs_exist_ok=True)

    kernel_params = " ".join(
        [
            "vga=788",
            "auto=true",
            "preseed/file=/cdrom/preseed.cfg",
            f"preseed/file/checksum={preseed_checksum}",
            "languagechooser/language-name=English",
            "countrychooser/shortlist=DE",
            "console-keymaps-at/keymap=de",
        ]
    )

    _logger.info("Patching GRUB / ISOLINUX")
    copytree(DATA_DIR / "grub", extracted_iso_dir / "boot" / "grub", dirs_exist_ok=True)
    copytree(DATA_DIR / "isolinux", extracted_iso_dir / "isolinux", dirs_exist_ok=True)
    for file in [
        extracted_iso_dir / "boot" / "grub" / "grub.cfg",
        extracted_iso_dir / "isolinux" / "txt.cfg",
    ]:
        file.write_text(file.read_text().replace("$KERNEL_PARAMS", kernel_params))


def _repack_iso(
    distro_name: str, distro_version: str, architecture: str, extracted_iso_dir: Path, output_directory: Path
) -> Path:
    version = get_version()
    output_file_path = (
        output_directory / f"voraus-runtime-{version}-{distro_name}-{distro_version}-{architecture}-headless.iso"
    )
    output_directory.mkdir(parents=True, exist_ok=True)

    _logger.info("Re-packing customized ISO")
    execute_command(
        [
            "xorriso",
            "-as",
            "mkisofs",
            "-r",
            "-V",
            f"{distro_name.capitalize()} {distro_version} {architecture}",
            "-o",
            str(output_file_path),
            "-J",
            "-J",
            "-joliet-long",
            "-cache-inodes",
            "-isohybrid-mbr",
            str(MBR_FILE),
            "-b",
            "isolinux/isolinux.bin",
            "-c",
            "isolinux/boot.cat",
            "-boot-load-size",
            "4",
            "-boot-info-table",
            "-no-emul-boot",
            "-eltorito-alt-boot",
            "-e",
            "boot/grub/efi.img",
            "-no-emul-boot",
            "-isohybrid-gpt-basdat",
            "-isohybrid-apm-hfsplus",
            str(extracted_iso_dir),
        ]
    )
    _logger.info(f"ISO has been written to {output_file_path}")
    return output_file_path
