"""Download ESEF-files."""

from __future__ import annotations

import os
from pathlib import Path
import zipfile

import requests

from pyesef.download.api_extractor import api_to_filing_record_list
from pyesef.log import LOGGER
from pyesef.utils.decorators import retry

from .common import Filing


def is_valid_zip(file_path: str) -> bool:
    """Return True if file is a valid ZIP file."""
    try:
        with zipfile.ZipFile(file_path, "r") as zip_ref:
            # Check if the zip file is valid
            zip_ref.testzip()
            return True
    except zipfile.BadZipFile:
        return False


@retry()
def _download_and_verify_package(filing: Filing) -> None:
    """
    Download a package and store it the archive-folder.

    Verify that it's a valid ZIP, or delete the file.
    """
    Path(filing.download_folder).mkdir(
        parents=True,
        exist_ok=True,
    )

    LOGGER.info(f"Downloading {filing.file_url}")

    # The file already exists, do an early return
    if os.path.exists(filing.write_location):
        LOGGER.info(f"File {filing.file_url} already exists, skipping")
        return

    req = requests.get(filing.file_url, stream=True, timeout=30)
    with open(filing.write_location, "wb") as _file:
        for chunk in req.iter_content(chunk_size=2048):
            _file.write(chunk)

    if not is_valid_zip(filing.write_location):
        LOGGER.warning(f"{filing.write_location} not a valid zip, deleting")
        os.remove(filing.write_location)


def download_packages() -> None:
    """Download XBRL-packages from XBRL.org."""
    data_list = api_to_filing_record_list()

    LOGGER.info(f"{len(data_list)} items found")

    for idx, item in enumerate(data_list):
        if idx % 10 == 0:
            LOGGER.info(f"Parsing {idx}/{len(data_list)}")

        _download_and_verify_package(item)
