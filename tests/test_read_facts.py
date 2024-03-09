"""Placeholder test."""

from datetime import datetime

import pytest

from pyesef.helpers.read_facts import (
    _get_is_extension,
    _get_is_total,
    _get_label,
    _get_membership,
    _get_period_end,
    _get_statement_item_group,
    _get_statement_type,
)


def test_get_label():
    """Test function _get_label."""
    property_view = (
        ("a", "b"),
        ("label", "bb"),
        ("c", "c"),
    )
    assert _get_label(property_view) == "bb"


def test_get_is_extension():
    """Test function _get_is_extension."""
    assert _get_is_extension("US GAAP") is True
    assert _get_is_extension("ifrs-full") is False


def test_get_period_end():
    """Test function _get_period_end."""
    end_date_time = datetime(2021, 1, 1)
    assert _get_period_end(end_date_time).year == 2020
    assert _get_period_end(end_date_time).month == 12
    assert _get_period_end(end_date_time).day == 31


def test_get_membership():
    """Test function _get_membership."""
    function_val = _get_membership(scenario=None)
    assert function_val == (
        None,
        None,
    )

    class ModelObject:
        """Mock scenario."""

        def __init__(self, value) -> None:
            self.stringValue = value  # pylint: disable=invalid-name

    test_object = ModelObject(value="a")
    function_val = _get_membership(test_object)

    assert function_val == (
        None,
        None,
    )

    test_object = ModelObject(value="a:b")
    function_val = _get_membership(test_object)

    assert function_val == ("a", "b")


def test_get_statement_type():
    """Test function _get_statement_type."""
    assert (
        _get_statement_type(
            xml_name_parent="CurrentAssets",
            xml_name="ABC",
        )
        == "balance_sheet"
    )


@pytest.mark.parametrize(
    "test_value, expected_result",
    [
        ("ProfitLoss", True),
        ("RevenueFromSaleOfGoods", False),
    ],
)
def test_get_is_total(test_value: str, expected_result: bool):
    """Test function _get_is_total."""
    summation_items = ["ProfitLoss"]

    function_value = _get_is_total(xml_name=test_value, summation_items=summation_items)

    assert function_value is expected_result


@pytest.mark.parametrize(
    "test_value, expected_result",
    [
        (
            "RevenueFromContractsWithCustomers",
            (
                "Revenue",
                True,
            ),
        ),
        (
            "OtherIncome",
            (
                "Revenue",
                True,
            ),
        ),
        (
            "CostOfMerchandiseSold",
            (
                "CostOfSales",
                True,
            ),
        ),
        (
            "ABC",
            (
                None,
                False,
            ),
        ),
    ],
)
def test_get_statement_item_group(test_value: str, expected_result: tuple[str, bool]):
    """Test function _get_is_total."""
    function_value = _get_statement_item_group(test_value)

    assert function_value[0] == expected_result[0]
    assert function_value[1] == expected_result[1]
