"""Constants."""
import os
import pathlib

PATH_BASE = pathlib.Path(__file__).parent.resolve()

PATH_FILINGS = os.path.join(PATH_BASE, "filings")
PATH_ARCHIVES = os.path.join(PATH_BASE, "archives")
PATH_NOT_VALID = os.path.join(PATH_BASE, "not_valid")
