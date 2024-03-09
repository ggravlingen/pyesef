"""Helper function to read facts."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from enum import Enum
import fractions
from typing import Any, cast

from arelle.ModelDtsObject import ModelConcept
from arelle.ModelInstanceObject import ModelContext, ModelFact
from arelle.ModelObject import ModelObject
from arelle.ModelValue import QName, dateTime
from arelle.ModelXbrl import ModelXbrl
from arelle.ValidateXbrlCalcs import roundValue

from pyesef.load_parse_file.common import EsefData

from ..const import NORMALISED_STATEMENT_MAP, STATEMENT_ITEM_GROUP_MAP, NiceType
from ..error import PyEsefError
from ..helpers.extract_definitions_to_csv import (
    check_definitions_exists,
    extract_definitions_to_csv,
)


class BaseXBRLiType(Enum):
    """Representation of baseXbrliType."""

    BOOLEAN = "booleanItemType"
    DATE = "dateItemType"


def parsed_value(
    fact: ModelFact,
) -> fractions.Fraction | int | Any | bool | str | None:
    """
    Parse value.

    Based on:
    https://github.com/private-circle/rlq/blob/master/rlq/rl_utils.py
    """
    if fact is None:
        return None

    concept: ModelConcept | None = fact.concept

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

    if concept.baseXbrliType == BaseXBRLiType.DATE:
        return dateTime(val)

    if concept.baseXbrliType == BaseXBRLiType.BOOLEAN:
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


def _get_is_total(xml_name: str, summation_items: list[str]) -> bool:
    """Return true if the item is a sum of other items."""
    return xml_name in summation_items


def _get_statement_type(
    xml_name_parent: str,
    xml_name: str,
) -> str:
    """Convert statement type raw into a normalised format."""
    if xml_name_parent in NORMALISED_STATEMENT_MAP:
        return NORMALISED_STATEMENT_MAP[xml_name_parent]

    if xml_name in NORMALISED_STATEMENT_MAP:
        return NORMALISED_STATEMENT_MAP[xml_name]

    return f"Unmatched: {xml_name}"


def _get_statement_item_group(xml_name: str) -> tuple[str | None, bool]:
    """Get statement item group name."""
    if xml_name in STATEMENT_ITEM_GROUP_MAP:
        return STATEMENT_ITEM_GROUP_MAP[xml_name], True

    return None, False


def _get_legal_name(facts: list[Any]) -> str | None:
    """Get legal name of entity."""
    for fact in facts:
        if fact.attrib["name"] == "ifrs-full:NameOfUltimateParentOfGroup":
            return cast(str, parsed_value(fact))

        if fact.attrib["name"] == "ifrs-full:NameOfParentEntity":
            return cast(str, parsed_value(fact))

    return None


def _get_sign_multiplier(balance: str) -> int:
    """Return multiplier to get correct sign for value."""
    if balance == "credit":
        return 1

    return -1


def _get_parent(xml_name: str, hierarchy_dict: dict[str, str]) -> str | None:
    """Get the parent of the item, if any."""
    if xml_name in hierarchy_dict:
        return hierarchy_dict[xml_name]

    return None


def read_facts(
    model_xbrl: ModelXbrl,
    summation_items: list[str],
    hierarchy_dict: dict[str, str],
) -> list[EsefData]:
    """Read facts of XBRL-files."""
    fact_list: list[EsefData] = []
    model_xbrl_fact_list: list[ModelFact] = model_xbrl.facts

    legal_name = _get_legal_name(facts=model_xbrl.facts)
    model_xbrl.modelManager.cntlr.addToLog(f"Entity: {legal_name}")

    for fact in model_xbrl_fact_list:
        concept: ModelConcept | None = fact.concept
        context: ModelContext | None = fact.context

        try:
            if concept is None or context is None:
                continue

            # We don't want to save meta data like company name etc
            if fact.localName == "nonNumeric" or concept.niceType in [
                NiceType.PER_SHARE,
                NiceType.SHARES,
            ]:
                continue

            date_period_end = _get_period_end(end_date_time=context.endDatetime)

            qname: QName = concept.qname

            # The name of the item, eg ComprehensiveIncome
            xml_name: str = qname.localName

            xml_name_parent = _get_parent(
                xml_name=xml_name, hierarchy_dict=hierarchy_dict
            )

            if xml_name_parent is None:
                statement_type = None
            else:
                statement_type = _get_statement_type(
                    xml_name_parent=xml_name_parent,
                    xml_name=xml_name,
                )

            # On the first run, we want to make sure we have all the definitions
            # cached locally
            if not check_definitions_exists():
                extract_definitions_to_csv(concept=concept)

            _, lei = context.entityIdentifier
            _, membership_name = _get_membership(context.scenario)
            statement_item_group, has_resolved_group = _get_statement_item_group(
                xml_name=xml_name
            )

            value = parsed_value(fact)

            if value is None:
                continue

            value = cast(int, value)
            value_multiplier: int = _get_sign_multiplier(concept.balance)

            fact_list.append(
                EsefData(
                    label=_get_label(fact.propertyView),
                    legal_name=legal_name,
                    xml_name=xml_name,
                    xml_name_parent=xml_name_parent,
                    statement_item_group=statement_item_group,
                    has_resolved_group=has_resolved_group,
                    statement_type=statement_type,
                    membership=membership_name,
                    value=value * value_multiplier,
                    is_extension=_get_is_extension(qname.prefix),
                    period_end=date_period_end,
                    lei=lei,
                    currency=fact.unit.value,
                    is_total=_get_is_total(
                        xml_name=xml_name,
                        summation_items=summation_items,
                    ),
                )
            )
        except Exception as exc:
            raise PyEsefError(f"Unable to parse fact {fact} ", exc) from exc

    return fact_list
