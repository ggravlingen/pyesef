"""Common functions and constants."""

from dataclasses import dataclass
from datetime import date
import fractions
from typing import Any


@dataclass
class EsefData:
    """Represent ESEF data as a dataclass."""

    # A date representing the end of the record's period
    period_end: date
    # The lei of the entity
    lei: str
    # The legal name of the entity
    legal_name: str | None
    # The lookup of the wider anchor, or the XML name if None
    wider_anchor_or_xml_name: str
    # The formal XBRL name of a company specified item
    wider_anchor: str | None
    # The XML name of the record item
    xml_name: str
    # # Currency of the value
    currency: str
    # Nominal value (in currency) of the record
    # Adjusted for debit/credit
    value: fractions.Fraction | int | Any | bool | str | None
    # Nominal value (in currency) of the record
    raw_value: fractions.Fraction | int | Any | bool | str | None
    # True if the record has been defined by the company
    is_company_defined: bool
    # The name of the item this record belongs to
    membership: str | None
    # The stated name of the record item
    xml_name_parent: str | None
    # The parent of the stated name of the record item
    label: str | None
    # A representation of the order of the item in the XBRL file
    sort_order: int

    # Will be output to JSON object
    __add_to_dict__ = [
        "is_cash_flow",
        "is_balance_sheet_maybe",
        "is_income_statement_maybe",
    ]

    @property
    def is_cash_flow(self) -> bool:
        """Return true if the item represent a cash flow igem."""
        return bool(self.xml_name_parent and "CashFlow" in self.xml_name_parent)

    @property
    def is_balance_sheet_maybe(self) -> bool:
        """
        Return True if the item represent a balance sheet item.

        Experimental, may bot be 100% correct.
        """
        return bool(
            self.xml_name_parent
            and (
                "Liabilities" in self.xml_name_parent
                or "Assets" in self.xml_name_parent
                or "Equity" in self.xml_name_parent
            )
        )

    @property
    def is_income_statement_maybe(self) -> bool:
        """
        Return True if the item represents an income statement item.

        Experimental, may bot be 100% correct.
        """
        return not self.is_cash_flow and not self.is_balance_sheet_maybe
