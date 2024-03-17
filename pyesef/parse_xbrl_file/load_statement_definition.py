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
from pyesef.parse_xbrl_file.common import clean_linkrole
from pyesef.parse_xbrl_file.read_and_save_filings import Controller, ReadFiling


def clean_ifrs(xml_tag: str) -> str:
    """Remove ifrs from tag."""
    cleaned_from_ifrs = xml_tag.replace("ifrs-full}", "")
    clean_other = cleaned_from_ifrs.replace("esef_cor}", "")
    return clean_other


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
        self.save_dict_to_json()

    @cached_property
    def base_taxonomy(self) -> ModelXbrl:
        """Return the base taxonomy model XBRL."""
        return ReadFiling.load_model_xbrl(
            zip_file_path=self.PATH_LINK_ROLE_XML, cntlr=self.cntlr
        )

    def load_cashflow(self) -> None:
        """Load all cash flow items."""
        base_taxonomy_cash_flow_rels = self.base_taxonomy.relationshipSet(
            parentChild, LinkRoleDefinition.CASH_FLOW
        )

        base_taxonomy_clarks = {
            clean_linkrole(clean_ifrs(rel.toModelObject.qname.clarkNotation))
            for rel in base_taxonomy_cash_flow_rels.modelRelationships
        }
        for root in base_taxonomy_cash_flow_rels.rootConcepts:
            base_taxonomy_clarks.add(
                clean_linkrole(clean_ifrs(root.qname.clarkNotation))
            )

        self.output_data_dict["cash_flow"] = list(base_taxonomy_clarks)

    def load_balance_sheet(self) -> None:
        """Load all balance sheet items."""
        base_taxonomy_cash_flow_rels = self.base_taxonomy.relationshipSet(
            parentChild, LinkRoleDefinition.BALANCE_SHEET
        )

        base_taxonomy_clarks = {
            clean_linkrole(clean_ifrs(rel.toModelObject.qname.clarkNotation))
            for rel in base_taxonomy_cash_flow_rels.modelRelationships
        }
        for root in base_taxonomy_cash_flow_rels.rootConcepts:
            base_taxonomy_clarks.add(
                clean_linkrole(clean_ifrs(root.qname.clarkNotation))
            )

        self.output_data_dict["balance_sheet"] = list(base_taxonomy_clarks)

    def load_income_statement(self) -> None:
        """Load all income statement items."""
        base_taxonomy_cash_flow_rels = self.base_taxonomy.relationshipSet(
            parentChild, LinkRoleDefinition.INCOME_STATEMENT
        )

        base_taxonomy_clarks = {
            clean_linkrole(clean_ifrs(rel.toModelObject.qname.clarkNotation))
            for rel in base_taxonomy_cash_flow_rels.modelRelationships
        }
        for root in base_taxonomy_cash_flow_rels.rootConcepts:
            base_taxonomy_clarks.add(
                clean_linkrole(clean_ifrs(root.qname.clarkNotation))
            )

        self.output_data_dict["income_statement"] = list(base_taxonomy_clarks)

    def save_dict_to_json(self) -> None:
        """Save data dict to JSON file."""
        with open(self.PATH_JSON_MAP_FILE, "w", encoding="UTF-8") as json_file:
            json.dump(self.output_data_dict, json_file)
