"""Tests for read and save filings."""

from datetime import date

from pyesef.helpers.read_and_save_filings import data_list_to_clean_df
from pyesef.load_parse_file.common import EsefData


def test_data_list_to_clean_df__drop_duplicates() -> None:
    """Test drop dupliates part of function data_list_to_clean_df."""
    function_result = data_list_to_clean_df(
        data_list=[
            EsefData(
                period_end=date(2023, 12, 31),
                lei="lei123",
                wider_anchor_or_xml_name="GainsLossesOnDisposalsOfInvestmentProperties",
                xml_name="GainsLossesOnDisposalsOfInvestmentProperties",
                xml_name_parent="ProfitLossBeforeTax",
                value=-1577000.0,
                raw_value=-1577000.0,
                legal_name=None,
                wider_anchor=None,
                membership=None,
                label=None,
                currency="SEK",
                is_company_defined=False,
                sort_order=1,
            ),
            EsefData(
                period_end=date(2023, 12, 31),
                lei="lei123",
                wider_anchor_or_xml_name="GainsLossesOnDisposalsOfInvestmentProperties",
                xml_name="GainsLossesOnDisposalsOfInvestmentProperties",
                xml_name_parent="ProfitLossBeforeTax",
                value=-1577000.0,
                raw_value=-1577000.0,
                legal_name=None,
                wider_anchor=None,
                membership=None,
                label=None,
                currency="SEK",
                is_company_defined=False,
                sort_order=1,
            ),
        ]
    )
    assert len(function_result) == 1
