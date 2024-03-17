"""Tests for read and save filings."""

from datetime import date
import os
from unittest.mock import patch

from pyesef.parse_xbrl_file.common import EsefData
from pyesef.parse_xbrl_file.read_and_save_filings import (
    ReadFiling,
    data_list_to_clean_df,
)
from pyesef.parse_xbrl_file.save_excel import SaveToExcel


def test_data_list_to_clean_df__drop_duplicates() -> None:
    """Test drop dupliates part of function data_list_to_clean_df."""
    function_result = data_list_to_clean_df(
        data_list=[
            EsefData(
                period_end=date(2023, 12, 31),
                lei="lei123",
                wider_anchor_or_xml_name="GainsLossesOnDisposalsOfInvestmentProperties",
                xml_name="GainsLossesOnDisposalsOfInvestmentProperties",
                value=-1577000.0,
                wider_anchor=None,
                membership=None,
                label=None,
                currency="SEK",
                is_company_defined=False,
                level_1="ComprehensiveIncome",
            ),
            EsefData(
                period_end=date(2023, 12, 31),
                lei="lei123",
                wider_anchor_or_xml_name="GainsLossesOnDisposalsOfInvestmentProperties",
                xml_name="GainsLossesOnDisposalsOfInvestmentProperties",
                value=-1577000.0,
                wider_anchor=None,
                membership=None,
                label=None,
                currency="SEK",
                is_company_defined=False,
                level_1="ComprehensiveIncome",
            ),
        ]
    )
    assert len(function_result) == 1


def test_read_and_save_filings() -> None:
    """Test read_and_save_filings."""
    with patch(
        "pyesef.parse_xbrl_file.read_and_save_filings.PATH_ARCHIVES",
        os.path.abspath(os.path.join("tests", "fixtures")),
    ):
        ReadFiling(should_move_parsed_file=False)
        assert os.path.exists(SaveToExcel.TEMPLATE_OUTPUT_PATH_EXCEL)
