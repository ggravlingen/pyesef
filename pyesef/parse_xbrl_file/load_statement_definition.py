"""
Testing.

Based on https://gist.github.com/AustinMatherne/f9a101ff48298f5b97b26e7f6e28833b
"""

from enum import StrEnum
from functools import cached_property
import json
import os

from arelle import PluginManager
from arelle.ModelXbrl import ModelXbrl
from arelle.XbrlConst import parentChild

from pyesef.const import PATH_PROJECT_ROOT

from .common import Controller, StatementName, load_model_xbrl


class LinkRoleDefinition(StrEnum):
    """Define link role definitions."""

    BALANCE_SHEET = "http://www.esma.europa.eu/xbrl/role/all/ias_1_role-210000"
    CASH_FLOW = "http://www.esma.europa.eu/xbrl/role/all/ias_7_role-520000"
    CHANGES_EQUITY = "http://www.esma.europa.eu/xbrl/role/all/ias_1_role-610000"
    INCOME_STATEMENT = "http://www.esma.europa.eu/xbrl/role/all/ias_1_role-310000"


class UpdateStatementDefinitionJson:
    """Load link roles into static data."""

    PATH_LINK_ROLE_XML = os.path.join(
        PATH_PROJECT_ROOT, "pyesef", "static", "taxonomy_2021-03-24", "esef_all-cal.xml"
    )
    PATH_JSON_MAP_FILE = os.path.join(
        PATH_PROJECT_ROOT, "pyesef", "static", "statement_definition.json"
    )

    def __init__(self) -> None:
        """Init class."""
        self.output_data_dict: dict[str, list[str]] = {}

        self.cntlr = Controller()

        # Add support for reading ESEF-files
        PluginManager.addPluginModule("validate/ESEF")

        self.main()

    def main(self) -> None:
        """Run sequence of methods."""
        self.load_cashflow()
        self.load_balance_sheet()
        self.load_income_statement()
        self.load_changes_equity()
        self.save_dict_to_json()

    @cached_property
    def base_taxonomy(self) -> ModelXbrl:
        """Return the base taxonomy model XBRL."""
        return load_model_xbrl(zip_file_path=self.PATH_LINK_ROLE_XML, cntlr=self.cntlr)

    def _loop_rel_set(self, link_role_definition: str) -> set[str]:
        """Loop through relationship set."""
        base_taxonomy_rels = self.base_taxonomy.relationshipSet(
            parentChild, link_role_definition
        )

        base_taxonomy_clarks = {
            rel.toModelObject.qname.clarkNotation
            for rel in base_taxonomy_rels.modelRelationships
        }
        for root in base_taxonomy_rels.rootConcepts:
            base_taxonomy_clarks.add(root.qname.clarkNotation)

        return base_taxonomy_clarks

    def load_cashflow(self) -> None:
        """Load all cash flow items."""
        self.output_data_dict[StatementName.CASH_FLOW.value] = list(
            self._loop_rel_set(LinkRoleDefinition.CASH_FLOW.value)
        )

    def load_balance_sheet(self) -> None:
        """Load all balance sheet items."""
        self.output_data_dict[StatementName.BALANCE_SHEET.value] = list(
            self._loop_rel_set(LinkRoleDefinition.BALANCE_SHEET.value)
        )

    def load_income_statement(self) -> None:
        """Load all income statement items."""
        self.output_data_dict[StatementName.INCOME_STATEMENT.value] = list(
            self._loop_rel_set(LinkRoleDefinition.INCOME_STATEMENT.value)
        )

    def load_changes_equity(self) -> None:
        """Load all changes in equity items."""
        self.output_data_dict[StatementName.CHANGES_EQUITY.value] = list(
            self._loop_rel_set(LinkRoleDefinition.CHANGES_EQUITY.value)
        )

    def save_dict_to_json(self) -> None:
        """Save data dict to JSON file."""
        with open(self.PATH_JSON_MAP_FILE, "w", encoding="UTF-8") as json_file:
            json.dump(self.output_data_dict, json_file)
