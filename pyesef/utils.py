"""Util functions."""
from __future__ import annotations

from dataclasses import asdict
import os
from typing import Any, Dict, cast

import jstyleson
import pandas as pd

from .const import PATH_ARCHIVES, PATH_BASE, PATH_FAILED, PATH_PARSED


def to_dataframe(data_list: list[Any]) -> pd.DataFrame:
    """Convert a list of filing data to a Pandas dataframe."""
    return pd.json_normalize(asdict(obj) for obj in data_list)


def get_item_description(
    local_name: str, lookup_table: dict[str, dict[str, str]]
) -> str | None:
    """Get the formal description of a line item."""
    if local_name in lookup_table:
        return (
            lookup_table[local_name]["definition"]
            # Make sure the descriptions don't contain line breaks
            .replace("\r", "").replace("\n", "")
        )

    return None


def move_file_to_parsed(file: str) -> None:
    """Move a file from the filings folder to the parsed folder."""
    os.replace(os.path.join(PATH_ARCHIVES, file), os.path.join(PATH_PARSED, file))


def move_file_to_error(file: str) -> None:
    """Move a file from the filings folder to the error folder."""
    os.replace(os.path.join(PATH_ARCHIVES, file), os.path.join(PATH_FAILED, file))


def _read_json(filename: str) -> dict[str, str]:
    """Open and read a json-file and return as a dict."""
    with open(os.path.join(PATH_BASE, filename), "rb") as _file:
        contents = _file.read()
        return cast(Dict[str, str], jstyleson.loads(contents))
