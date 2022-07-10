"""Placeholder test."""
from pyesef.helpers.read_facts import _get_label


def test_test():
    """Just a placeholder test."""
    property_view = (
        ("a", "b"),
        ("label", "bb"),
        ("c", "c"),
    )
    assert _get_label(property_view) == "bb"
