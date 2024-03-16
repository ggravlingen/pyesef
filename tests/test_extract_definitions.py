"""Tests for helper to extract definitions."""

from pyesef.helpers.extract_definitions_to_csv import (
    _get_definition,
    _get_label,
    _get_label_xml,
)

TEST_DATA = (
    (
        "label",
        "Abnormally large changes in asset prices or foreign exchange rates [member]",
        (
            [
                (
                    "documentation (en)",
                    (
                        "The axis of a table defines the relationship between the "
                        "members in the table and the line items or concepts that "
                        "complete the table."
                    ),
                ),
                (
                    "documentation (sv)",
                    (
                        "Axeln i en tabell anger förhållandet mellan elementen i "
                        "tabellen och posterna eller begreppen som kompletterar "
                        "tabellen."
                    ),
                ),
                ("label (en)", "Accounting estimates [axis]"),
                ("label (sv)", "Uppskattningar och bedömningar [axis]"),
            ]
        ),
    ),
    ("namespace", "http://xbrl.ifrs.org/taxonomy/2021-03-24/ifrs-full"),
    ("name", "AbnormallyLargeChangesInAssetPricesOrForeignExchangeRatesMember"),
    (
        "QName",
        "ifrs-full:AbnormallyLargeChangesInAssetPricesOrForeignExchangeRatesMember",
    ),
    ("id", "ifrs-full_AbnormallyLargeChangesInAssetPricesOrForeignExchangeRatesMember"),
    ("abstract", "true"),
    ("type", "nonnum:domainItemType"),
    ("subst grp", "xbrli:item"),
    ("period type", "duration"),
    (),
    (
        "facets",
        "length",
    ),
    (
        "references",
        (
            "IAS 10 2021-01-01 22 g http://eifrs.ifrs.org/eifrs/xifrs-link?type=IAS&"
            "num=10&code=ifrs-tx-2021-en-r&anchor=para_22_g&doctype=Standard 2021-03-24"
        ),
    ),
)


def test_get_label_xml():
    """Test function _get_label_xml."""
    function_value = _get_label_xml(TEST_DATA)
    assert (
        function_value
        == "AbnormallyLargeChangesInAssetPricesOrForeignExchangeRatesMember"
    )


def test_get_label():
    """Test function _get_label."""
    function_value = _get_label(TEST_DATA)
    assert (
        function_value
        == "Abnormally large changes in asset prices or foreign exchange rates [member]"
    )


def test_get_definition():
    """Test function _get_definition."""
    function_value = _get_definition(TEST_DATA)
    assert function_value == (
        "The axis of a table defines the relationship between the members in the "
        "table and the line items or concepts that complete the table."
    )
