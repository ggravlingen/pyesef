"""Constants."""
from __future__ import annotations

from enum import Enum
import os
import pathlib

PATH_BASE = pathlib.Path(__file__).parent.resolve()

PATH_ARCHIVES = os.path.join(PATH_BASE, "archives")
PATH_FILINGS = os.path.join(PATH_BASE, "filings")
PATH_PARSED = os.path.join(PATH_BASE, "parsed")
PATH_PROJECT_ROOT = os.path.join(PATH_BASE, "..")

FILE_ENDING_XML = ".xhtml"

CSV_SEPARATOR = "|"


class FileName(str, Enum):
    """Representation of files that may be available in the XBRL-folder."""

    CATALOG = "catalog.xml"
    TAXONOMY_PACKAGE = "taxonomyPackage.xml"
    TAXONOMY_PACKAGE_DOT = ".taxonomyPackage.xml"


class NiceType(str, Enum):
    """Representation of different types of 'nice types'."""

    PER_SHARE = "PerShare"
    SHARES = "Shares"


STANDARD_ROLE_MAP = {
    "ias_1_role-110000": "General information about financial statements",
    "ias_1_role-210000": "Statement of financial position, current/non-current",
    "ias_1_role-220000": "Statement of financial position, order of liquidity",
    "ias_1_role-310000": "Statement of comprehensive income, profit or loss, by function of expense",
    "ias_1_role-320000": "Statement of comprehensive income, profit or loss, by nature of expense",
    "ias_1_role-410000": "Statement of comprehensive income, OCI components presented net of tax",
    "ias_1_role-420000": "Statement of comprehensive income, OCI components presented before tax",
    "ias_1_role-510000": "Statement of cash flows, direct method",
    "ias_1_role-520000": "Statement of cash flows, indirect method",
    "ias_1_role-610000": "Statement of changes in equity",
    "ias_1_role-710000": "Statement of changes in net assets available for benefits",
}


class StatementType(Enum):
    """Representation of statement types."""

    GENERAL = "general_information"
    BS = "balance_sheet"
    IS = "income_statement"
    CF = "cash_flow_statement"
    OCI = "other_comprehensive_income"
    OCI_AT = "other_comprehensive_income_after_tax"
    OCI_PT = "other_comprehensive_income_pre_tax"
    EQ = "changes_equity"


# It appears companies may define role names freely. This is a mapping from the
# companies' role name to a standardised name.
NORMALISED_STATEMENT_MAP = {
    # General items
    "ias_1_role-110000": StatementType.GENERAL.value,
    # Balance sheet
    "ias_1_role-210000": StatementType.BS.value,
    "ias_1_role-220000": StatementType.BS.value,
    "RapportOEverFinansiellStaellning": StatementType.BS.value,
    "Rapportöverfinansiellställningförkoncernen": StatementType.BS.value,
    "StatementOfFinancialPosition": StatementType.BS.value,
    "FinancialPosition": StatementType.BS.value,
    "BalanceSheet": StatementType.BS.value,
    "EgetKapitalOchSkulder": StatementType.BS.value,
    "Tillgangar": StatementType.BS.value,
    "ConsolidatedStatementsOfFinancialPosition": StatementType.BS.value,
    "FinancialPositionGroup": StatementType.BS.value,
    "ConsolidatedBalanceSheets": StatementType.BS.value,
    "Balansräkningkoncernen": StatementType.BS.value,
    "FinancialPosition2": StatementType.BS.value,
    # Income statement
    "ias_1_role-310000": StatementType.IS.value,
    "ias_1_role-320000": StatementType.IS.value,
    "RapportOEverTotalresultat": StatementType.IS.value,
    "IncomeStatement": StatementType.IS.value,
    "ProfitOrLoss": StatementType.IS.value,
    "ProfitAndLoss": StatementType.IS.value,
    "Resultat": StatementType.IS.value,
    "Roerelseresultat": StatementType.IS.value,
    "Rapportöverresultatochövrigttotalresultatförkoncernen": StatementType.IS.value,
    "IncomeStatement2": StatementType.IS.value,
    "ConsolidatedStatementsOfOperations": StatementType.IS.value,
    "IncomeStatementGroup": StatementType.IS.value,
    "ConsolidatedStatementsOfIncome": StatementType.IS.value,
    "AnalysAvIntaekterOchKostnader": StatementType.IS.value,
    "Resultaträkningkoncernen": StatementType.IS.value,
    "ConsolidatedStatementsOfIncomeLossAndComprehensiveIncome": StatementType.IS.value,
    # Other comprehensive income
    "ias_1_role-410000": StatementType.OCI_AT.value,
    "ConsolidatedStatementsOfTotalEquity": StatementType.OCI_AT.value,
    "ias_1_role-420000": StatementType.OCI_PT.value,
    "ComprehensiveIncome": StatementType.OCI.value,
    "StatementOfComprehensiveIncome": StatementType.OCI.value,
    "RapportOEverTotalresultat1": StatementType.OCI.value,
    "ComprehensiveIncome2": StatementType.OCI.value,
    "ConsolidatedStatementsOfComprehensiveIncomeLoss": StatementType.OCI.value,
    "ComprehensiveIncomeGroup": StatementType.OCI.value,
    "ConsolidatedStatementsOfComprehensiveIncome": StatementType.OCI.value,
    "RapportOEverTotalresultat3": StatementType.OCI.value,
    "OtherComprehensiveIncome": StatementType.OCI.value,
    "StatementOfComprehensiveIncome1": StatementType.OCI.value,
    "OCI": StatementType.OCI.value,
    "RapportOEverTotalresultat2": StatementType.OCI.value,
    # Cash flow statement
    "ias_1_role-510000": StatementType.CF.value,
    "ias_1_role-520000": StatementType.CF.value,
    "ias_7_role-520000": StatementType.CF.value,
    "RapportOEverKassafloeden": StatementType.CF.value,
    "Rapportöverkassaflödenförkoncernen": StatementType.CF.value,
    "CashFlow": StatementType.CF.value,
    "StatementOfCashFlows": StatementType.CF.value,
    "ConsolidatedStatementsOfCashFlows": StatementType.CF.value,
    "Kassaflödesanalyskoncernen": StatementType.CF.value,
    "KassaflödesanalyskoncernenParentheticals1": StatementType.CF.value,
    # Changes in equity
    "ias_1_role-610000": StatementType.EQ.value,
    "RapportOEverFoeraendringarIEgetKapital": StatementType.EQ.value,
    "ChangesinEquity": StatementType.EQ.value,
    "RapportOEverFoeraendringarIEgetKapital5": StatementType.EQ.value,
    "RapportOEverFoeraendringarIEgetKapital6": StatementType.EQ.value,
    "RapportOEverFoeraendringarIEgetKapital8": StatementType.EQ.value,
    "ChangesinEquity2": StatementType.EQ.value,
    "StatementOfChangesInEquity": StatementType.EQ.value,
    "StatementOfChangesInEquity7": StatementType.EQ.value,
    "ChangesinEquityPrevious": StatementType.EQ.value,
    "RapportOEverFoeraendringarIEgetKapital2": StatementType.EQ.value,
}

# A list of XML-names that represent a summation line
LOCAL_NAME_KNOWN_TOTAL: list[str] = [
    # Income statement
    "GrossProfit",
    "FinanceIncomeCost",
    "ProfitLossBeforeTax",
    "ProfitLoss",
    "ProfitLossFromOperatingActivities",
    "ProfitLossAttributableToOwnersOfParent",
    "FinanceCosts",
    "EBITDA",
    # Balance sheet
    "CurrentAssets",
    "NoncurrentAssets",
    "Assets",
    "NoncurrentLiabilities",
    "CurrentLiabilities",
    "Liabilities",
    "EquityAndLiabilities",
    # Cash flow
    "CashFlowsFromUsedInOperatingActivities",
    "CashFlowsFromUsedInOperationsBeforeChangesInWorkingCapital",
    "CashFlowsFromUsedInInvestingActivities",
    "CashFlowBeforeFinancing",
    "CashFlowsFromUsedInFinancingActivities",
]
