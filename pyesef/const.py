"""Constants."""

from __future__ import annotations

from enum import Enum
import os
import pathlib
from typing import Final

PATH_BASE = pathlib.Path(__file__).parent.resolve()
PATH_PROJECT_ROOT = os.path.abspath(os.path.join(PATH_BASE, ".."))

PATH_ARCHIVES = os.path.abspath(os.path.join(PATH_PROJECT_ROOT, "archives"))
PATH_PARSED = os.path.abspath(os.path.join(PATH_PROJECT_ROOT, "parsed"))
PATH_FAILED = os.path.abspath(os.path.join(PATH_PROJECT_ROOT, "error"))

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


# We have to use .value here, else the value stored in the CSV becomes
# eg StatementType.IS instead of income_statement.
NORMALISED_STATEMENT_MAP: Final[dict[str, str]] = {
    # Income statement
    "ProfitLossFromOperatingActivities": StatementType.IS.value,
    "OperatingExpense": StatementType.IS.value,
    "FinanceIncomeCost": StatementType.IS.value,
    "GrossProfit": StatementType.IS.value,
    "RevenueFromSaleOfOilAndGasProductsAndRoyaltyExpense": StatementType.IS.value,
    "ProfitLossBeforeTax": StatementType.IS.value,
    "ProfitLoss": StatementType.IS.value,
    "ProfitLossAttributableToOwnersOfParent": StatementType.IS.value,
    # Other comprehensive income
    "OtherComprehensiveIncome": StatementType.OCI.value,
    "ComprehensiveIncome": StatementType.OCI.value,
    "ComprehensiveIncomeAttributableToOwnersOfParent": StatementType.OCI.value,
    "OtherComprehensiveIncomeBeforeTax": StatementType.OCI.value,
    "ComprehensiveIncomeAttributableToNoncontrollingInterests": StatementType.OCI.value,
    "ItemsInComprehensiveIncome": StatementType.OCI.value,
    # Balance sheet
    "NoncurrentAssets": StatementType.BS.value,
    "CurrentAssets": StatementType.BS.value,
    "TradeAndOtherCurrentReceivables": StatementType.BS.value,
    "Assets": StatementType.BS.value,
    "Equity": StatementType.BS.value,
    "NoncurrentLiabilities": StatementType.BS.value,
    "CurrentLiabilities": StatementType.BS.value,
    "EquityAndLiabilities": StatementType.BS.value,
    "IntangibleAssetsAndGoodwill": StatementType.BS.value,
    "PropertyPlantAndEquipment": StatementType.BS.value,
    "NoncurrentReceivables": StatementType.BS.value,
    "Inventories": StatementType.BS.value,
    "TotalEquity": StatementType.BS.value,
    "TradeAndOtherReceivables": StatementType.BS.value,
    # Cash flow
    "CashFlowsFromUsedInOperationsBeforeChangesInWorkingCapital": StatementType.CF.value,  # pylint: disable=line-too-long # noqa: E501
    "CashFlowsFromUsedInOperatingActivities": StatementType.CF.value,
    "CashFlowsFromUsedInInvestingActivities": StatementType.CF.value,
    "CashFlowsFromUsedInFinancingActivities": StatementType.CF.value,
    "IncreaseDecreaseInCashAndCashEquivalents": StatementType.CF.value,
    "IncreaseDecreaseInWorkingCapital": StatementType.CF.value,
    "IncreaseDecreaseInCashAndCashEquivalentsBeforeEffectOfExchangeRateChanges": StatementType.CF.value,  # pylint: disable=line-too-long # noqa: E501
    "EffectOfExchangeRateChangesOnCashAndCashEquivalents": StatementType.CF.value,
    # Statement of equity
    "IncreaseDecreaseThroughTransactionsWithOwners": StatementType.EQ.value,
    "DividendsRecognisedAsDistributionsToOwnersOfParentRelatingToPriorYears": StatementType.EQ.value,  # pylint: disable=line-too-long # noqa: E501
    "ShareIssueRelatedCost": StatementType.EQ.value,
    "IncreaseDecreaseThroughOtherContributionsByOwners": StatementType.EQ.value,
    "IncreaseDecreaseThroughSharebasedPaymentTransactions": StatementType.EQ.value,
    "IncreaseDecreaseThroughExerciseOfOptions": StatementType.EQ.value,
    "EquityAttributableToOwnersOfParent": StatementType.EQ.value,
    "DividendsPaid": StatementType.EQ.value,
    "IssueOfEquity": StatementType.EQ.value,
    "DividendsRecognisedAsDistributionsToOwnersOfParent": StatementType.EQ.value,
    "DividendsRecognisedAsDistributionsToNoncontrollingInterests": StatementType.EQ.value,  # pylint: disable=line-too-long # noqa: E501
    "IncreaseDecreaseThroughTransfersAndOtherChangesEquity": StatementType.EQ.value,
}


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
    "IntangibleAssetsOtherThanGoodwill": "IntangibleAssetsOtherThanGoodwill",
    # PPE
    "Land": "PropertyPlantAndEquipment",
    "MachineryAndEquipment": "PropertyPlantAndEquipment",
    "RightofuseAssets": "PropertyPlantAndEquipment",
    "ConstructionInProgress": "PropertyPlantAndEquipment",
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
    "GeneralAndAdministrativeExpense": "SellingGeneralAndAdministrativeExpense",
    "SellingGeneralAndAdministrativeExpense": "SellingGeneralAndAdministrativeExpense",
    "OtherExpenseByNature": "SellingGeneralAndAdministrativeExpense",
    "EmployeeBenefitsExpense": "SellingGeneralAndAdministrativeExpense",
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
    "CurrentTaxExpenseIncome": "CurrentTaxes",
}
