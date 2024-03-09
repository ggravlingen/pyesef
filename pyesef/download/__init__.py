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

        if len(filing_list) == 1:
            data_list.append(filing_list[0])
            continue

        for filing in filing_list:
            if "en" in filing.file_name:
                data_list.append(filing)
                continue

    return data_list


def _download_package(filing: Filing) -> None:
    """Download a package and store it the archive-folder."""
    url = f"{BASE_URL}{filing.path}/{filing.file_name}"

    download_path = os.path.join(PATH_ARCHIVES, filing.country)

    # Create download path if it does not exist
    Path(download_path).mkdir(parents=True, exist_ok=True)

    LOGGER.info(f"Downloading {url}")

    req = requests.get(url, stream=True, timeout=30)
    write_location = os.path.join(download_path, filing.file_name)
    with open(write_location, "wb") as _file:
        for chunk in req.iter_content(chunk_size=2048):
            _file.write(chunk)


def download_packages() -> None:
    """
    Download XBRL-packages from XBRL.org.

    Prefer the English version of there are multiple languages available.
    """
    identifier_map: IdentifierType = {}
    idx: int = 0

    with urllib.request.urlopen(f"{BASE_URL}table-index.json") as url:
        data = json.loads(url.read().decode())
        for _, item in enumerate(data):
            if item["country"] in [
                Country.DENMARK,
                Country.FINLAND,
                Country.ICELAND,
                Country.NORWAY,
                Country.SWEDEN,
            ]:
                lei = item["lei"]
                filing = Filing(
                    country=_extract_alpha_2_code(path=item["path"]),
                    file_name=item["report-package"],
                    path=item["path"],
                )

                if lei not in identifier_map:
                    identifier_map[lei] = [filing]
                else:
                    identifier_map[lei].append(filing)

    data_list = _cleanup_package_dict(identifier_map=identifier_map)

    LOGGER.info(f"{len(data_list)} items found")

    for idx, item in enumerate(data_list):
        if idx % 10 == 0:
            LOGGER.info(f"Parsing {idx}/{len(data_list)}")

        _download_package(item)
