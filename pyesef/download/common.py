"""Common."""

from dataclasses import dataclass
from enum import StrEnum
import os

from pyesef.parse_xbrl_file.read_and_save_filings import PATH_ARCHIVES

BASE_URL = "https://filings.xbrl.org/"


class Country(StrEnum):
    """Representation of different countries."""

    DENMARK = "DK"
    FINLAND = "FI"
    ICELAND = "IS"
    NORWAY = "NO"
    SWEDEN = "SE"


@dataclass
class Filing:
    """Version 2 of a filing record."""

    country_iso_2: str
    package_url: str
    period_end: str
    lei: str

    @property
    def file_url(self) -> str:
        """Return file URL."""
        return f"{BASE_URL}/{self.package_url}"

    @property
    def download_folder(self) -> str:
        """Return download path."""
        return os.path.join(
            PATH_ARCHIVES,
            self.country_iso_2,
        )

    @property
    def file_name(self) -> str:
        """Return file name."""
        splitted_string = self.package_url.split("/")
        return splitted_string[-1]

    @property
    def write_location(self) -> str:
        """Return file write location."""
        return os.path.join(
            self.download_folder,
            self.file_name,
        )
