"""Util functions."""
from __future__ import annotations

from dataclasses import asdict
import os
import shutil
from typing import Any

import pandas as pd

from .const import PATH_PARSED


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


def move_file_to_parsed(entry: os.DirEntry) -> None:
    """Move a file from the filings folder to the parsed folder."""
    parsed_folder = os.path.join(PATH_PARSED, entry.name)

    if os.path.exists(parsed_folder):
        shutil.rmtree(parsed_folder)
    shutil.move(
        entry,
        PATH_PARSED,
    )
