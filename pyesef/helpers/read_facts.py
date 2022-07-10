"""Helper function to read facts."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
import fractions
from typing import Any

from arelle import ModelXbrl
from arelle.ModelDtsObject import ModelConcept
from arelle.ModelInstanceObject import ModelFact
from arelle.ModelValue import dateTime
from arelle.ValidateXbrlCalcs import roundValue


@dataclass
class EsefData:
    """Represent ESEF data as a dataclass."""

    # The lei of the entity
    lei: str
    # A date representing the end of the record's period
    period_end: date
    # The stated name of the record item
    label: str | None
    # The XML name of the record item
    local_name: str
    # The name of the item this record belongs to
    membership: str | None
    # Currency of the value
    currency: str
    # Nominal value (in currency) of the record
    value: fractions.Fraction | int | Any | bool | str | None
    # Type of period. Duration for income statement and cf, instant for balance sheet
    period_type: str
    # Denote if the record is debit or credit
    debit_or_credit: str
    # Prefix for the record's name
    prefix: str
    # Prefix for the record's parent
    membership_prefix: str | None
    # True if the record has been defined by the company
    is_extension: bool = False


def parsed_value(
    fact: ModelFact,
) -> (fractions.Fraction | int | Any | bool | str | None):
    """
    Parse value.

    https://github.com/private-circle/rlq/blob/master/rlq/rl_utils.py
    """
    if fact is None:
        return None

    concept: ModelConcept = fact.concept

    if concept is None or concept.isTuple or fact.isNil:
        return None

    if concept.isFraction:
        num, den = map(fractions.Fraction, fact.fractionValue)
        return num / den

    val = fact.value.strip()

    if concept.isInteger:
        return int(val)
    elif concept.isNumeric:
        dec = fact.decimals

        if dec is None or dec == "INF":  # show using decimals or reported format
            dec = len(val.partition(".")[2])
        else:  # max decimals at 28
            dec = max(
                min(int(dec), 28), -28
            )  # 2.7 wants short int, 3.2 takes regular int, don't use _INT here
        num = roundValue(val, fact.precision, dec)  # round using reported decimals
        return num
    elif concept.baseXbrliType == "dateItemType":
        return dateTime(val)
    elif concept.baseXbrliType == "booleanItemType":
        return val.lower() in ("1", "true")
    elif concept.isTextBlock:
        return " ".join(val.split())
    return val


def _get_label(property_view: tuple[tuple[str, str]]) -> str | None:
    """Extract label."""
    for item in property_view:
        if item[0] == "label":
            return item[1]

    return None


def _get_membership(scenario: str | None) -> tuple[str, str] | tuple[None, None]:
    """Get membership of item."""
    if scenario is None:
        return None, None

    items = scenario.stringValue.split(":")
    if not items:
        return None, None

    return items[0], items[1]


def _get_is_extension(prefix: str) -> bool:
    """Return true if the record is not defined in the IFRS taxonomy."""
    return prefix != "ifrs-full"


def _get_period_end(end_date_time: datetime) -> date:
    """Return the end of the fact's financial period."""
    return (end_date_time - timedelta(days=1)).date()


# TO:DO: IFRS description
# TO:DO: statement type


def read_facts(model_xbrl: ModelXbrl, filter_year: int | None = None) -> list[EsefData]:
    """Read facts of XBRL-files."""
    fact_list: list[EsefData] = []

    for fact in model_xbrl.facts:
        date_period_end = _get_period_end(end_date_time=fact.context.endDatetime)

        if filter_year is not None and date_period_end.year != filter_year:
            continue

        # We don't want to save meta data like company name etc
        if fact.localName == "nonNumeric" or fact.concept.niceType in [
            "PerShare",
            "Shares",
        ]:
            continue

        _, lei = fact.context.entityIdentifier
        membership_prefix, membership_name = _get_membership(fact.context.scenario)

        fact_list.append(
            EsefData(
                prefix=fact.qname.prefix,
                label=_get_label(fact.propertyView),
                local_name=fact.qname.localName,
                membership_prefix=membership_prefix,
                membership=membership_name,
                value=parsed_value(fact),
                is_extension=_get_is_extension(fact.qname.prefix),
                period_end=date_period_end,
                lei=lei,
                currency=fact.unit.value,
                period_type=fact.concept.periodType,
                debit_or_credit=fact.concept.balance,
            )
        )

    return fact_list
