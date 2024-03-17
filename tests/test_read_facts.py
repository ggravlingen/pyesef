"""Placeholder test."""

from datetime import datetime
from unittest.mock import Mock, patch

from pyesef.parse_xbrl_file.read_facts import (
    _get_is_extension,
    _get_label,
    _get_legal_name,
    _get_membership,
    _get_period_end,
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


@patch(
    "pyesef.load_parse_file.read_facts.parsed_value",
    return_value="NameOfUltimateParentOfGroup",
)
def test_get_legal_name_of_ultimate_parent(_mock_data):
    """Test function _get_legal_name."""
    facts = [
        Mock(
            attrib={"name": "ifrs-full:NameOfUltimateParentOfGroup"},
        ),
        Mock(
            attrib={
                "name": "ifrs-full:OtherFact",
            },
        ),
    ]
    result = _get_legal_name(facts)
    assert result == "NameOfUltimateParentOfGroup"


@patch(
    "pyesef.load_parse_file.read_facts.parsed_value",
    return_value="NameOfParentEntity",
)
def test_get_legal_name_of_parent_entity(_mock_data):
    """Test function _get_legal_name."""
    facts = [
        Mock(
            attrib={
                "name": "ifrs-full:NameOfParentEntity",
            },
        ),
    ]
    result = _get_legal_name(facts)
    assert result == "NameOfParentEntity"


@patch(
    "pyesef.load_parse_file.read_facts.parsed_value",
    return_value="NameOfParentEntity",
)
def test_get_legal_name__none(_mock_data):
    """Test function _get_legal_name."""
    facts = []
    result = _get_legal_name(facts)
    assert result is None
