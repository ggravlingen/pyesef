"""Utils."""

from __future__ import annotations

from dataclasses import asdict as std_asdict
from typing import Any

import pandas as pd


def asdict(obj):
    """
    Allow setting properties on a dataclass.

    From https://stackoverflow.com/a/64778375.
    """
    return {
        **std_asdict(obj),
        **{a: getattr(obj, a) for a in getattr(obj, "__add_to_dict__", [])},
    }


def data_list_to_clean_df(data_list: list[Any]) -> pd.DataFrame:
    """Convert a list of filing data to a Pandas dataframe."""
    data_frame_from_data_class = pd.json_normalize(  # type: ignore[arg-type]
        asdict(obj) for obj in data_list
    )

    data_frame_from_data_class["period_end"] = pd.to_datetime(
        data_frame_from_data_class["period_end"]
    )

    # Drop zero values
    data_frame_from_data_class = data_frame_from_data_class.query("value != 0")

    # Drop any duplicates
    data_frame_from_data_class = data_frame_from_data_class.drop_duplicates(
        subset=[
            "lei",
            "period_end",
            "wider_anchor_or_xml_name",
            "xml_name",
            "xml_name_parent",
        ],
        keep="last",
    )

    # Drop beginning-of-year items
    data_frame_from_data_class = data_frame_from_data_class.query(
        "not (period_end.dt.month == 1 & period_end.dt.day == 1)"
    )

    data_frame_from_data_class = data_frame_from_data_class.sort_values(
        ["lei", "period_end", "sort_order"],
    )

    return data_frame_from_data_class
