"""Constants."""
from __future__ import annotations

from enum import Enum
import os
import pathlib

PATH_BASE = pathlib.Path(__file__).parent.resolve()
PATH_PROJECT_ROOT = os.path.join(PATH_BASE, "..")

PATH_ARCHIVES = os.path.join(PATH_PROJECT_ROOT, "archives")
PATH_PARSED = os.path.join(PATH_PROJECT_ROOT, "parsed")
PATH_FAILED = os.path.join(PATH_PROJECT_ROOT, "error")

FILE_ENDING_ZIP = ".zip"

CSV_SEPARATOR = "|"


class NiceType(str, Enum):
    """Representation of different types of 'nice types'."""

    PER_SHARE = "PerShare"
    SHARES = "Shares"


STANDARD_ROLE_MAP = {
    "ias_1_role-110000": "General information about financial statements",
    "ias_1_role-210000": "Statement of financial position, current/non-current",
    "ias_1_role-220000": "Statement of financial position, order of liquidity",
    "ias_1_role-310000": (
        "Statement of comprehensive income, profit or loss, by function of expense"
    ),
    "ias_1_role-320000": (
        "Statement of comprehensive income, profit or loss, by nature of expense"
    ),
    "ias_1_role-410000": (
        "Statement of comprehensive income, OCI components presented net of tax"
    ),
    "ias_1_role-420000": (
        "Statement of comprehensive income, OCI components presented before tax"
    ),
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
NORMALISED_STATEMENT_MAP: dict[str, str] = {
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
    "Rapportövertotalresultatkoncernen": StatementType.IS.value,
    "ProfitOrLoss1": StatementType.IS.value,
    "AnalysAvIntaekterOchKostnader1": StatementType.IS.value,
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
    "TotalresultatFoerAret",
    "Totalincometax",
    "TotalRevenueOtherOperatingIncomeAndWorkPerformedByEntityAndCapitalised",
    "TotalRevenue",
    "TotalOtherExpensesIncome",
    "TotalOperatingExpensesExcludingDepreciationAndAmortisationExpense",
    "TotalOperatingExpensesBeforeCreditLosses",
    "TotalOperatingExpenses",
    "TotalOperatingCosts",
    "TotalFinancialItems",
    "TotalExpensesBeforeCreditLosses",
    "TotalExpenses",
    "InterestRevenueExpense",  # For banks
    "FeeAndCommissionIncomeExpense"  # For banks
    # Balance sheet
    "CurrentAssets",
    "NoncurrentAssets",
    "Assets",
    "NoncurrentLiabilities",
    "CurrentLiabilities",
    "Liabilities",
    "IntangibleAssetsAndGoodwill",
    "EquityAndLiabilities",
    "PropertyPlantAndEquipment",
    "Equity",
    "CurrentAssetsexcludingCash",
    "CurrentAssets",
    "NoncurrentAssets",
    # Cash flow
    "CashFlowsFromUsedInOperatingActivities",
    "CashFlowsFromUsedInOperationsBeforeChangesInWorkingCapital",
    "CashFlowsFromUsedInInvestingActivities",
    "CashFlowBeforeFinancing",
    "CashFlowsFromUsedInFinancingActivities",
]

STATEMENT_ITEM_GROUP_MAP: dict[str, str] = {
    # Cash and equivalents
    "BankOverdraftsClassifiedAsCashEquivalents": "CashAndCashEquivalents",
    "Cash": "CashAndCashEquivalents",
    "CashAndBankBalancesAtCentralBanks": "CashAndCashEquivalents",
    "CashAndCashEquivalents": "CashAndCashEquivalents",
    "CashEquivalents": "CashAndCashEquivalents",
    "CurrentAssetsexcludingCash": "CashAndCashEquivalents",
    "NoncurrentRestrictedCashAndCashEquivalents": "CashAndCashEquivalents",
    "OtherCashAndCashEquivalents": "CashAndCashEquivalents",
    "ShorttermDepositsClassifiedAsCashEquivalents": "CashAndCashEquivalents",
    "ShorttermDepositsNotClassifiedAsCashEquivalents": "CashAndCashEquivalents",
    "ShorttermInvestmentsClassifiedAsCashEquivalents": "CashAndCashEquivalents",
    # Payables
    "TradeAndOtherCurrentPayablesToRelatedParties": "CurrentPayables",
    "TradeAndOtherCurrentPayablesToTradeSuppliers": "CurrentPayables",
    # Intangibles
    "Goodwill": "IntangibleAssets",
    "IntangibleAssetsOtherThanGoodwill": "IntangibleAssets",
    # Equity
    "NoncontrollingInterests": "TotalEquity",
    "EquityAttributableToOwnersOfParent": "TotalEquity",
    # Revenue
    "OtherRevenue": "Revenue",
    "OtherIncome": "Revenue",
    "Revenue": "Revenue",
    "RevenueFromConstructionContracts": "Revenue",
    "RevenueFromContractsWithCustomers": "Revenue",
    "RevenueFromHotelOperations": "Revenue",
    "RevenueFromRenderingOfServices": "Revenue",
    "RevenueFromSaleOfGoods": "Revenue",
    "RevenueFromSaleOfOilAndGasProducts": "Revenue",
    "RevenueFromSaleOfOilAndGasProductsAndRoyaltyExpense": "Revenue",
    # Revenue | real estate
    "RentalIncome": "Revenue",
    "RentalIncomeFromInvestmentProperty": "Revenue",
    # Revenue | banks
    "InterestRevenueCalculatedUsingEffectiveInterestMethod": "Revenue",
    "InterestIncomeOnOtherFinancialAssets": "Revenue",
    # Cost of goods sold
    "CostOfSales": "CostOfSales",
    "CostOfMerchandiseSold": "CostOfSales",
    "CostOfGoodsSold": "CostOfSales",
    "RawMaterialsAndConsumablesUsed": "CostOfSales",
    "ProductionExpenses": "CostOfSales",
    "OperatingExpense": "CostOfSales",
    # Cost of goods sold | real estate
    "DirectOperatingExpenseFromInvestmentProperty": "CostOfSales",
    "DirectOperatingExpenseFromInvestmentPropertyGeneratingRentalIncome": "CostOfSales",
    "PropertyTaxExpense": "CostOfSales",
    # Cost of goods sold | bank
    "InterestExpense": "CostOfSales",
    # Net finance cost
    "FinanceIncome": "NetFinanceIncomeCost",
    "FinanceCosts": "NetFinanceIncomeCost",
    "ReclassificationAdjustmentsOnCashFlowHedgesBeforeTax": "NetFinanceIncomeCost",
    # SG&A
    "AdministrativeExpense": "SellingGeneralAndAdministrativeExpense",
    "OtherExpenseByFunction": "SellingGeneralAndAdministrativeExpense",
    "SellingGeneralAndAdministrativeExpense": "SellingGeneralAndAdministrativeExpense",
    # R&D
    "ResearchAndDevelopmentExpense": "ResearchAndDevelopmentExpense",
    # Marketing
    "SalesAndMarketingExpense": "SalesAndMarketingExpense",
    "SellingExpense": "SalesAndMarketingExpense",
    # Gains and losses
    "GainsLossesOnHedgesOfNetInvestmentsInForeignOperationsBeforeTax": "GainsLosses",
    "GainsLossesOnExchangeDifferencesOnTranslationBeforeTax": "GainsLosses",
    "GainsLossesOnCashFlowHedgesBeforeTax": "GainsLosses",
    # Taxes
    "IncomeTaxExpenseContinuingOperations": "CurrentTaxes",
}
