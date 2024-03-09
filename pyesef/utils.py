"""Util functions."""

from __future__ import annotations

from dataclasses import asdict
import os
from pathlib import Path
from typing import Any, cast

import jstyleson
import pandas as pd

from .const import PATH_BASE, PATH_FAILED, PATH_PARSED


def data_list_to_clean_df(data_list: list[Any]) -> pd.DataFrame:
    """Convert a list of filing data to a Pandas dataframe."""
    data_frame_from_data_class = pd.json_normalize(asdict(obj) for obj in data_list)  # type: ignore[arg-type]

    data_frame_from_data_class["period_end"] = pd.to_datetime(
        data_frame_from_data_class["period_end"]
    )

    # Drop zero values
    data_frame_from_data_class = data_frame_from_data_class.query("value != 0")

    # Drop any duplicates
    data_frame_from_data_class = data_frame_from_data_class.drop_duplicates(
        subset=["lei", "period_end", "wider_anchor_or_xml_name", "xml_name_parent"],
        keep="last",
    )

    # Drop beginning-of-year items
    # data_frame_from_data_class = data_frame_from_data_class.query(
    #     "not (period_end.dt.month == 1 & period_end.dt.day == 1)"
    # )

    data_frame_from_data_class = data_frame_from_data_class.sort_values(
        ["lei", "period_end", "sort_order"],
    )

    return data_frame_from_data_class


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


def _read_json(filename: str) -> dict[str, str]:
    """Open and read a json-file and return as a dict."""
    with open(os.path.join(PATH_BASE, filename), "rb") as _file:
        contents = _file.read()
        return cast(dict[str, str], jstyleson.loads(contents))
