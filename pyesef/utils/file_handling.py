"""File handling utils."""

from __future__ import annotations

import os
from pathlib import Path
from typing import cast
import zipfile

import jstyleson

from pyesef.const import PATH_BASE, PATH_FAILED, PATH_PARSED


def is_valid_zip(file_path: str) -> bool:
    """Return True if file is a valid ZIP file."""
    try:
        with zipfile.ZipFile(file_path, "r") as zip_ref:
            # Check if the zip file is valid
            zip_ref.testzip()
            return True
    except zipfile.BadZipFile:
        return False


def move_file_to_parsed(zip_file_path: str, language: str) -> None:
    """Move a file from the filings folder to the parsed folder."""
    final_path = os.path.join(PATH_PARSED, language)
    Path(final_path).mkdir(parents=True, exist_ok=True)

    os.replace(
        zip_file_path,
        os.path.join(final_path, os.path.basename(zip_file_path)),
    )


def move_file_to_error(zip_file_path: str, language: str) -> None:
    """Move a file from the filings folder to the error folder."""
    final_path = os.path.join(PATH_FAILED, language)
    Path(final_path).mkdir(parents=True, exist_ok=True)

    os.replace(
        zip_file_path,
        os.path.join(final_path, os.path.basename(zip_file_path)),
    )


def read_json(filename: str) -> dict[str, str]:
    """Open and read a json-file and return as a dict."""
    with open(os.path.join(PATH_BASE, filename), "rb") as _file:
        contents = _file.read()
        return cast(dict[str, str], jstyleson.loads(contents))
