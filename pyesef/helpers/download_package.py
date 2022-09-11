"""Helper function to download a XBRL-package."""
from dataclasses import dataclass
import json
import os
from pathlib import Path
import urllib.request

import requests

from ..const import PATH_ARCHIVES, Country

BASE_URL = "https://filings.xbrl.org/"


@dataclass
class Filing:
    """Represent a filing."""

    country: str
    file_name: str
    path: str


IdentifierType = dict[str, list[Filing]]


def _parse_file_ending(path: str) -> str:
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


def download_packages() -> None:
    """
    Download XBRL-packages from XBRL.org.

    Prefer the English version of there are multiple languages available.
    """
    identifier_map: IdentifierType = {}
    idx: int = 0

    with urllib.request.urlopen(f"{BASE_URL}table-index.json") as url:
        data = json.loads(url.read().decode())
        for idx, item in enumerate(data):
            if item["country"] in [
                # Country.DENMARK,
                # Country.FINLAND,
                # Country.ICELAND,
                # Country.NORWAY,
                Country.SWEDEN,
            ]:

                lei = item["lei"]
                filing = Filing(
                    country=_parse_file_ending(path=item["path"]),
                    file_name=item["report-package"],
                    path=item["path"],
                )

                if lei not in identifier_map:
                    identifier_map[lei] = [filing]
                else:
                    identifier_map[lei].append(filing)

    data_list = _cleanup_package_dict(identifier_map=identifier_map)

    print(f"{len(data_list)} items found")

    for idx, item in enumerate(data_list):
        if idx % 10 == 0:
            print(f"Parsing {idx}/{len(data_list)}")

        _download_package(item)


def _download_package(filing: Filing) -> None:
    """Download a package and store it the archive-folder."""
    url = f"{BASE_URL}{filing.path}/{filing.file_name}"

    download_path = os.path.join(PATH_ARCHIVES, filing.country)

    # Create download path if it does not exist
    Path(download_path).mkdir(parents=True, exist_ok=True)

    print(f"Downloading {url}")

    req = requests.get(url, stream=True, timeout=30)
    write_location = os.path.join(download_path, filing.file_name)
    with open(write_location, "wb") as _file:
        for chunk in req.iter_content(chunk_size=2048):
            _file.write(chunk)
