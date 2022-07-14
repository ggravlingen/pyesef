"""Helper function to download a XBRL-package."""
import json
import os
import urllib.request

import requests

from ..const import PATH_ARCHIVES

BASE_URL = "https://filings.xbrl.org/"


def download_packages() -> None:
    """Download XBRL-packages from XBRL.org."""
    data_list: list[dict[str, str]] = []
    identifier_list: list[str] = []
    with urllib.request.urlopen(f"{BASE_URL}table-index.json") as url:
        data = json.loads(url.read().decode())
        for idx, item in enumerate(data):
            if item["country"] == "SE":
                identifier = item["report-package"].split("-")[0]

                if identifier not in identifier_list:
                    identifier_list.append(identifier)
                    data_list.append(
                        {"file_name": item["report-package"], "path": item["path"]}
                    )

    for item in data_list:
        _download_package(item)

    print(f"{idx} items found")


def _download_package(item: dict[str, str], chunk_size: int = 128) -> None:
    """Download a package and store in arhive-folder."""
    url = f"{BASE_URL}{item['path']}/{item['file_name']}"
    req = requests.get(url, stream=True)
    write_location = os.path.join(PATH_ARCHIVES, item["file_name"])
    with open(write_location, "wb") as fd:
        for chunk in req.iter_content(chunk_size=chunk_size):
            fd.write(chunk)
