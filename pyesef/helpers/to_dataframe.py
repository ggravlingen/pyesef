"""Converter."""
from __future__ import annotations

from dataclasses import asdict

import pandas as pd

from .read_facts import EsefData


def to_dataframe(filing_list: list[EsefData]) -> pd.DataFrame:
    """Convert a list of filing data to a Pandas dataframe."""
    return pd.json_normalize(asdict(obj) for obj in filing_list)
