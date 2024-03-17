"""Helper function to read facts."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from enum import Enum
import fractions
from typing import Any, cast

from arelle import XbrlConst
from arelle.ModelDtsObject import ModelConcept, ModelRelationship
from arelle.ModelInstanceObject import ModelContext, ModelFact
from arelle.ModelObject import ModelObject
from arelle.ModelValue import QName, dateTime
from arelle.ModelXbrl import ModelXbrl
from arelle.ValidateXbrlCalcs import roundValue

from pyesef.load_parse_file.common import EsefData

from ..const import NiceType
from ..error import PyEsefError


class BaseXBRLiType(Enum):
    """Representation of baseXbrliType."""

    BOOLEAN = "booleanItemType"
    DATE = "dateItemType"


ROLE_TO_STATEMENT_TYPE_MAP = {
    # Balance sheet
    "ConsolidatedBalanceSheets": "BalanceSheet",
    "EgetKapitalOchSkulder": "BalanceSheet",
    "ias_1_role-210000": "BalanceSheet",
    "ias_1_role-210000_extended": "BalanceSheet",
    "ias_1_role-220000": "BalanceSheet",
    "FinancialPosition": "BalanceSheet",
    "KoncernensBalansrkning": "BalanceSheet",
    "Koncernensbalansraekning": "BalanceSheet",
    "Rapportöverfinansiellställningförkoncernen": "BalanceSheet",
    "RapportverFinansiellStllningFrKoncernen": "BalanceSheet",
    "RapportOEverFinansiellStaellning": "BalanceSheet",
    "StatementOfFinancialPosition": "BalanceSheet",
    "StatementoffinancialpositioncurrentnoncurrentStatement": "BalanceSheet",
    "Table1StatementOfFinancialPositionAbstract": "BalanceSheet",
    "Tillgangar": "BalanceSheet",
    # Cash flow
    "ias_7_role-520000": "CashFlow",
    "ias_7_role-520000_extended": "CashFlow",
    "CashFlowStatement": "CashFlow",
    "ConsolidatedStatementsOfCashFlows": "CashFlow",
    "KassafldesanalysFrKoncernen": "CashFlow",
    "Koncernenskassafloedesanalys": "CashFlow",
    "RapportOEverKassafloeden": "CashFlow",
    "Rapportöverkassaflödenförkoncernen": "CashFlow",
    "StatementOfCashFlows": "CashFlow",
    "Table1StatementOfCashFlowsAbstract": "CashFlow",
    "StatementofcashflowsindirectmethodStatement": "CashFlow",
    # Changes in equity
    "ChangesinEquity": "ChangesEquity",
    "ChangesinEquity2": "ChangesEquity",
    "ConsolidatedStatementsOfChangesInEquity": "ChangesEquity",
    "ias_1_role-610000": "ChangesEquity",
    "ias_1_role-610000_extended": "ChangesEquity",
    "RapportOEverFoeraendringarIEgetKapital": "ChangesEquity",
    "SammanstllningverFrndringAvEgetKapitalIKoncernen": "ChangesEquity",
    "StatementofchangesinequityStatement": "ChangesEquity",
    # Income statement
    "ConsolidatedStatementsOfComprehensiveIncomeLoss": "IncomeStatement",
    "ConsolidatedStatementsOfOperations": "IncomeStatement",
    "ComprehensiveIncome": "IncomeStatement",
    "IncomeStatement": "IncomeStatement",
    "IncomeStatement2": "IncomeStatement",
    "ias_1_role-310000": "IncomeStatement",
    "ias_1_role-310000_extended": "IncomeStatement",
    "ias_1_role-320000": "IncomeStatement",
    "ias_1_role-320000_extended": "IncomeStatement",
    "ias_1_role-410000": "IncomeStatement",
    "ias_1_role-410000_extended": "IncomeStatement",
    "ias_1_role-420000": "IncomeStatement",
    "KoncernensResultatrkningOchvrigtTotalresultat": "IncomeStatement",
    "KoncernensRapportverTotalresultatAlternate1": "IncomeStatement",
    "KoncernensRapportverTotalresultat": "IncomeStatement",
    "Koncernensrapportoevertotalresultat": "IncomeStatement",
    "KoncernensResultatrkning": "IncomeStatement",
    "KoncernensResultatrkningAlternate1": "IncomeStatement",
    "ProfitOrLoss": "IncomeStatement",
    "ProfitLoss": "IncomeStatement",
    "RapportOEverTotalresultat": "IncomeStatement",
    "RapportOEverTotalresultat2": "IncomeStatement",
    "Rapportöverresultatochövrigttotalresultatförkoncernen": "IncomeStatement",
    "Resultat": "IncomeStatement",
    "StatementOfComprehensiveIncome": "IncomeStatement",
    "StatementOfComprehensiveIncome2": "IncomeStatement",
    "Table1ProfitOrLossAbstract": "IncomeStatement",
    "Table1StatementOfComprehensiveIncomeAbstract": "IncomeStatement",
    "StatementofcomprehensiveincomeOCIcomponentspresentednetoftaxStatement": (
        "IncomeStatement"
    ),
    "StatementofcomprehensiveincomeOCIcomponentspresentednetoftaxStatement_1": (
        "IncomeStatement"
    ),
    "StatementofcomprehensiveincomeprofitorlossbyfunctionofexpenseStatement": (
        "IncomeStatement"
    ),
    "StatementofcomprehensiveincomeprofitorlossbyfunctionofexpenseStatement_1": (
        "IncomeStatement"
    ),
    "StatementofcomprehensiveincomeprofitorlossbynatureofexpenseStatement": (
        "IncomeStatement"
    ),
    "StatementofcomprehensiveincomeprofitorlossbynatureofexpenseStatement_1": (
        "IncomeStatement"
    ),
}


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


def _get_legal_name(facts: list[Any]) -> str | None:
    """Get legal name of entity."""
    for fact in facts:
        if fact.attrib["name"] == "ifrs-full:NameOfUltimateParentOfGroup":
            return cast(str, parsed_value(fact))

        if fact.attrib["name"] == "ifrs-full:NameOfParentEntity":
            return cast(str, parsed_value(fact))

    return None


def _wider_anchor_to_dict(model_xbrl: ModelXbrl) -> dict[str, Any]:
    """Extract map of XML names from wider anchor."""
    output_map: dict[str, str] = {}
    wide_narrow_relationship: list[ModelRelationship] = model_xbrl.relationshipSet(
        XbrlConst.widerNarrower
    ).modelRelationships
    for relation in wide_narrow_relationship:
        cleaned_from_list = str(relation.toModelObject.qname).split(":")
        cleaned_to_list = str(relation.fromModelObject.qname).split(":")

        company_defined_name = cleaned_from_list[1]
        formal_name = cleaned_to_list[1]

        if company_defined_name not in output_map:
            output_map[company_defined_name] = formal_name

    return output_map


def facts_to_data_list(
    model_xbrl: ModelXbrl,
    to_model_to_linkrole_map: dict[str, str],
) -> list[EsefData]:
    """Read facts of XBRL-files."""
    fact_list: list[EsefData] = []
    model_xbrl_fact_list: list[ModelFact] = model_xbrl.facts

    legal_name = _get_legal_name(facts=model_xbrl.facts)
    model_xbrl.modelManager.cntlr.addToLog(f"Entity: {legal_name}")

    wider_anchor_map = _wider_anchor_to_dict(model_xbrl=model_xbrl)

    for fact in model_xbrl_fact_list:
        concept: ModelConcept | None = fact.concept
        context: ModelContext | None = fact.context

        try:
            if concept is None or context is None:
                continue

            # We don't want to save meta data like company name etc
            if fact.localName == "nonNumeric" or concept.niceType in [
                NiceType.PER_SHARE.value,
                NiceType.SHARES.value,
            ]:
                continue

            date_period_end = _get_period_end(end_date_time=context.endDatetime)

            qname: QName = concept.qname

            # The name of the item, eg ComprehensiveIncome
            xml_name: str = qname.localName

            if wider_anchor_map.get(xml_name, False):
                wider_anchor = wider_anchor_map[xml_name]
            else:
                wider_anchor = None

            _, lei = context.entityIdentifier
            _, membership_name = _get_membership(context.scenario)

            value = parsed_value(fact)

            if value is None:
                continue

            if wider_anchor is None:
                wider_anchor_or_xml_name = xml_name
            else:
                wider_anchor_or_xml_name = wider_anchor

            value = cast(int, value)

            if xml_name in to_model_to_linkrole_map:
                xml_level_1_key = to_model_to_linkrole_map[xml_name]
            else:
                xml_level_1_key = None

            level_1: str | None
            if xml_level_1_key and xml_level_1_key in ROLE_TO_STATEMENT_TYPE_MAP:
                level_1 = ROLE_TO_STATEMENT_TYPE_MAP[xml_level_1_key]
            else:
                level_1 = xml_level_1_key

            fact_list.append(
                EsefData(
                    period_end=date_period_end,
                    lei=lei,
                    wider_anchor_or_xml_name=wider_anchor_or_xml_name,
                    wider_anchor=wider_anchor,
                    xml_name=xml_name,
                    currency=fact.unit.value,
                    value=value,
                    is_company_defined=_get_is_extension(qname.prefix),
                    membership=membership_name,
                    label=_get_label(fact.propertyView),
                    level_1=level_1,
                )
            )
        except Exception as exc:
            raise PyEsefError(f"Unable to parse fact {fact} ", exc) from exc

    return fact_list
