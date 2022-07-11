"""Util functions."""
from __future__ import annotations

from dataclasses import asdict
from typing import Any

import pandas as pd


def to_dataframe(data_list: list[Any]) -> pd.DataFrame:
    """Convert a list of filing data to a Pandas dataframe."""
    return pd.json_normalize(asdict(obj) for obj in data_list)
