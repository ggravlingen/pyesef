"""Converter."""
from __future__ import annotations

import pandas as pd

from .read_filings import FilingData


def to_dataframe(filing_list: list[FilingData]) -> pd.DataFrame:
    """Convert a list of filing data to a Pandas dataframe."""
    df_list: list = []

    for filing in filing_list:
        for fact in filing.facts:
            df_list.append(
                {
                    "lei": filing.lei,
                    "period_end": filing.period_end,
                    "prefix": fact.prefix,
                    "name": fact.local_name,
                    "value": fact.value,
                    "is_extension": fact.is_extension,
                }
            )

    return pd.DataFrame(df_list)
