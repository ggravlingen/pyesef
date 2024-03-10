"""Download ESEF-files."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import json
import os
from pathlib import Path
import urllib.request

import requests

from pyesef.log import LOGGER
from pyesef.utils.file_handling import is_valid_zip

from ..const import PATH_ARCHIVES

BASE_URL = "https://filings.xbrl.org/"


class Country(str, Enum):
    """Representation of different countries."""

    DENMARK = "DK"
    FINLAND = "FI"
    ICELAND = "IS"
    NORWAY = "NO"
    SWEDEN = "SE"


@dataclass
class Filing:
    """Represent a filing."""

    country: str
    file_name: str
    path: str

    @property
    def file_url(self) -> str:
        """Return file URL."""
        return f"{BASE_URL}{self.path}/{self.file_name}"

    @property
    def download_country_folder(self) -> str:
        """Return download path."""
        return os.path.join(PATH_ARCHIVES, self.country)

    @property
    def write_location(self) -> str:
        """Return file write location."""
        return os.path.join(self.download_country_folder, self.file_name)


IdentifierType = dict[str, list[Filing]]


def _extract_alpha_2_code(path: str) -> str:
    """Parse the file ending."""
    path = path.lower()
    splitted_path = path.split("/")
    country_iso = splitted_path[-2]
    return country_iso


def _cleanup_package_dict(identifier_map: IdentifierType) -> list[Filing]:
    """
    Cleanup package dict and return only one filing.

    Will return the English version if available.
    """
    data_list: list[Filing] = []
    for key, _ in identifier_map.items():
        filing_list = identifier_map[key]

        for filing in filing_list:
            data_list.append(filing)

    return data_list


def _download_and_verify_package(filing: Filing) -> None:
    """
    Download a package and store it the archive-folder.

    Verify that it's a valid ZIP, or delete the file.
    """
    Path(  # Create download path if it does not exist
        filing.download_country_folder
    ).mkdir(
        parents=True,
        exist_ok=True,
    )

    LOGGER.info(f"Downloading {filing.file_url}")

    req = requests.get(filing.file_url, stream=True, timeout=30)
    with open(filing.write_location, "wb") as _file:
        for chunk in req.iter_content(chunk_size=2048):
            _file.write(chunk)

    if not is_valid_zip(filing.write_location):
        LOGGER.warning(f"{filing.write_location} not a valid zip, deleting")
        os.remove(filing.write_location)


def _create_filing_list() -> IdentifierType:
    """Return a list of filings."""
    identifier_map: IdentifierType = {}
    with urllib.request.urlopen(f"{BASE_URL}table-index.json") as url:
        data = json.loads(url.read().decode())
        for _, item in enumerate(data):

            # We're only interested in these countries for now
            if item["country"] not in [
                Country.DENMARK,
                Country.FINLAND,
                Country.ICELAND,
                Country.NORWAY,
                Country.SWEDEN,
            ]:
                continue

            lei = item["lei"]

            # This is a bit hacky, but should work
            # We guess that there is a ZIP-file for more years
            # than what is available in the JSON
            for year in [2021, 2022, 2023]:
                file_name = str(item["report-package"]).replace("2021", str(year))
                file_path = str(item["path"]).replace("2021", str(year))

                filing = Filing(
                    country=_extract_alpha_2_code(path=item["path"]),
                    file_name=file_name,
                    path=file_path,
                )

                if lei not in identifier_map:
                    identifier_map[lei] = [filing]
                else:
                    identifier_map[lei].append(filing)

    return identifier_map


def download_packages() -> None:
    """Download XBRL-packages from XBRL.org."""
    identifier_map = _create_filing_list()
    data_list = _cleanup_package_dict(identifier_map=identifier_map)

    LOGGER.info(f"{len(data_list)} items found")

    for idx, item in enumerate(data_list):
        if idx % 10 == 0:
            LOGGER.info(f"Parsing {idx}/{len(data_list)}")

        _download_and_verify_package(item)
