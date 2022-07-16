"""Helper function to read facts."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
import fractions
from typing import Any

from arelle.ModelDtsObject import ModelConcept
from arelle.ModelInstanceObject import ModelFact
from arelle.ModelObject import ModelObject
from arelle.ModelValue import QName, dateTime
from arelle.ModelXbrl import ModelXbrl
from arelle.ValidateXbrlCalcs import roundValue

from ..const import (
    LOCAL_NAME_KNOWN_TOTAL,
    NORMALISED_STATEMENT_MAP,
    NiceType,
    StatementType,
)
from .extract_definitions_to_csv import (
    check_definitions_exists,
    extract_definitions_to_csv,
)


@dataclass
class EsefData:
    """Represent ESEF data as a dataclass."""

    # The lei of the entity
    lei: str
    # A date representing the end of the record's period
    period_end: date
    # Type of statement in a normalised format
    statement_type: str | None
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
    # True if the record has been defined by the company
    is_extension: bool = False
    # True if the item is a sum of other items
    is_total: bool = False


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

    if concept.isNumeric:
        dec = fact.decimals

        if dec is None or dec == "INF":  # show using decimals or reported format
            dec = len(val.partition(".")[2])
        else:  # max decimals at 28
            dec = max(
                min(int(dec), 28), -28
            )  # 2.7 wants short int, 3.2 takes regular int, don't use _INT here
        num = roundValue(val, fact.precision, dec)  # round using reported decimals
        return num

    if concept.baseXbrliType == "dateItemType":
        return dateTime(val)

    if concept.baseXbrliType == "booleanItemType":
        return val.lower() in ("1", "true")

    if concept.isTextBlock:
        return " ".join(val.split())

    return val


def _get_label(property_view: tuple[tuple[str, str]]) -> str | None:
    """Extract label."""
    for item in property_view:
        if item[0] == "label":
            return item[1]

    return None


def _get_membership(
    scenario: ModelObject | None,
) -> tuple[str, str] | tuple[None, None]:
    """Get membership of item."""
    if scenario is None:
        return None, None

    items = scenario.stringValue.split(":")

    if not items or len(items) != 2:
        return None, None

    return items[0], items[1]


def _get_is_extension(prefix: str) -> bool:
    """Return true if the record is not defined in the IFRS taxonomy."""
    return prefix != "ifrs-full"


def _get_period_end(end_date_time: datetime) -> date:
    """Return the end of the fact's financial period."""
    return (end_date_time - timedelta(days=1)).date()


def _get_statement_type_raw(
    model_roles: dict[str, str], clark_notation: str
) -> str | None:
    """Determine what financial statement type an item belongs to."""
    if clark_notation in model_roles:
        return model_roles[clark_notation]

    return None


def _get_is_total(local_name: str) -> bool:
    """Return true if the item is a sum of other items."""
    return local_name in LOCAL_NAME_KNOWN_TOTAL


def _get_statement_type(statement_type_raw: str, xml_name: str) -> str:
    """Convert statement type raw into a normalised format."""
    if "Comprehensive" in xml_name:
        # Companies sometimes put OCI in the income statement.
        # We want to separate them so that's handled here.
        return StatementType.OCI.value

    if statement_type_raw in NORMALISED_STATEMENT_MAP:
        return NORMALISED_STATEMENT_MAP[statement_type_raw]

    return statement_type_raw


def read_facts(
    model_xbrl: ModelXbrl,
    model_roles: dict[str, str],
) -> list[EsefData]:
    """Read facts of XBRL-files."""
    fact_list: list[EsefData] = []

    for fact in model_xbrl.facts:
        date_period_end = _get_period_end(end_date_time=fact.context.endDatetime)

        qname: QName = fact.concept.qname

        statement_type_raw = _get_statement_type_raw(
            model_roles=model_roles, clark_notation=qname.clarkNotation
        )

        # The name of the item, eg ComprehensiveIncome
        xml_name: str = qname.localName

        if statement_type_raw is not None:
            statement_type = _get_statement_type(
                statement_type_raw=statement_type_raw, xml_name=xml_name
            )
        else:
            statement_type = None

        # On the first run, we want to make sure we have all the definitions
        # cached locally
        if not check_definitions_exists():
            extract_definitions_to_csv(concept=fact.concept)

        # We don't want to save meta data like company name etc
        if fact.localName == "nonNumeric" or fact.concept.niceType in [
            NiceType.PER_SHARE,
            NiceType.SHARES,
        ]:
            continue

        _, lei = fact.context.entityIdentifier
        _, membership_name = _get_membership(fact.context.scenario)

        fact_list.append(
            EsefData(
                label=_get_label(fact.propertyView),
                local_name=xml_name,
                statement_type=statement_type,
                membership=membership_name,
                value=parsed_value(fact),
                is_extension=_get_is_extension(qname.prefix),
                period_end=date_period_end,
                lei=lei,
                currency=fact.unit.value,
                is_total=_get_is_total(local_name=xml_name),
            )
        )

    return fact_list
