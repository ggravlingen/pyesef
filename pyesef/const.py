"""Constants."""
from enum import Enum
import os
import pathlib

PATH_BASE = pathlib.Path(__file__).parent.resolve()

PATH_FILINGS = os.path.join(PATH_BASE, "filings")
PATH_ARCHIVES = os.path.join(PATH_BASE, "archives")

FILE_ENDING_XML = ".xhtml"


class FileName(str, Enum):
    """Representation of files that may be available in the XBRL-folder."""

    CATALOG = "catalog.xml"
    TAXONOMY_PACKAGE = "taxonomyPackage.xml"
    TAXONOMY_PACKAGE_DOT = ".taxonomyPackage.xml"


class NiceType(str, Enum):
    """Representation of different types of 'nice types'."""

    PER_SHARE = "PerShare"
    SHARES = "Shares"
