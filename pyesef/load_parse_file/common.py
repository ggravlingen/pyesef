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
    # The lookup of the wider anchor, or the XML name if None
    wider_anchor_or_xml_name: str
    # The formal XBRL name of a company specified item
    wider_anchor: str | None
    # The XML name of the record item
    xml_name: str
    # # Currency of the value
    currency: str
    # Nominal value (in currency) of the record
    value: fractions.Fraction | int | Any | bool | str | None
    # True if the record has been defined by the company
    is_company_defined: bool
    # The name of the item this record belongs to
    membership: str | None
    # The parent of the stated name of the record item
    label: str | None
    # The type of statement (balance sheet, income statement or cash flow statement)
    level_1: str | None

    # Will be output to JSON object
    __add_to_dict__ = [
        "is_cash_flow",
        "is_balance_sheet",
        "is_income_statement",
        "is_changes_in_equity",
        "is_other",
        "is_total",
    ]

    @property
    def is_balance_sheet(self) -> bool:
        """Return True if the node is part of the balance sheet."""
        return self.level_1 == "BalanceSheet"

    @property
    def is_cash_flow(self) -> bool:
        """Return True if the node is part of the cash flow statement."""
        return self.level_1 == "CashFlow"

    @property
    def is_income_statement(self) -> bool:
        """Return True if the node is part of the income statement."""
        return self.level_1 == "IncomeStatement"

    @property
    def is_changes_in_equity(self) -> bool:
        """Retrun True if the node is part of the change in equity statement."""
        return self.level_1 == "ChangesEquity"

    @property
    def is_other(self) -> bool:
        """Return True is neither of cash flow, income statement or balance sheet."""
        return (
            not self.is_cash_flow
            and not self.is_balance_sheet
            and not self.is_income_statement
            and not self.is_changes_in_equity
        )

    @property
    def is_total(self) -> bool:
        """Return True if representing a total or sub-total."""
        return self.wider_anchor_or_xml_name in [
            # Cash flow statements
            "CashFlowsFromUsedInOperationsBeforeChangesInWorkingCapital",
            "CashFlowsFromUsedInOperatingActivities",
            "CashFlowsFromUsedInFinancingActivities",
            "CashFlowsFromUsedInInvestingActivities",
            "IncreaseDecreaseInCashAndCashEquivalents",
            "IncreaseDecreaseInCashAndCashEquivalentsBeforeEffectOfExchangeRateChanges",
            # Balance sheet items
            "NoncurrentAssets",
            "CurrentAssets",
            "Assets",
            "NoncurrentLiabilities",
            "CurrentLiabilities",
            # Removed for now, seems this is not used in a good way in XML-files
            # "Equity",
            "EquityAndLiabilities",
            # Income statement items
            "ProfitLossFromOperatingActivities",
            "ProfitLossBeforeTax",
            "ProfitLoss",
            "ComprehensiveIncome",
        ]
