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
    # Type of statement in a normalised format
    statement_type: str | None
    # False if no statement item group was matched
    has_resolved_group: bool
    # True if the record has been defined by the company
    is_extension: bool
    # True if the item is a sum of other items
    is_total: bool
    # The line item group the record belongs to
    statement_item_group: str | None
    # The XML name of the record item
    xml_name: str
    # The stated name of the record item
    xml_name_parent: str | None
    # The parent of the stated name of the record item
    label: str | None
    # The name of the item this record belongs to
    membership: str | None
    # Currency of the value
    currency: str
    # Nominal value (in currency) of the record
    value: fractions.Fraction | int | Any | bool | str | None
    # The lei of the entity
    lei: str
    # The legal name of the entity
    legal_name: str | None
