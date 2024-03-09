"""Constants."""

from __future__ import annotations

from enum import Enum
import os
import pathlib

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
