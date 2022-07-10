"""Helper function to unzip archives."""
import os
import zipfile

from ..const import PATH_ARCHIVES, PATH_FILINGS


def extract_filings() -> None:
    """Extract all files in archives folder."""
    for root, _, files in os.walk(PATH_ARCHIVES):
        for file in files:
            if file.endswith(".zip"):
                zip_file = f"{root}/{file}"
                with zipfile.ZipFile(zip_file, "r") as zip_ref:
                    zip_ref.extractall(PATH_FILINGS)
