"""Based on https://gist.github.com/AustinMatherne/f9a101ff48298f5b97b26e7f6e28833b."""

from functools import cached_property
import json
import os

from arelle import PluginManager
from arelle.ModelXbrl import ModelXbrl
from arelle.XbrlConst import parentChild

from pyesef.const import PATH_PROJECT_ROOT, PATH_STATIC

from .common import Controller, StatementName, load_model_xbrl


class LinkRoleDefinition:
    """Define link role definitions."""

    BALANCE_SHEET: set[str] = {
        "http://www.esma.europa.eu/xbrl/role/all/ias_1_role-210000",
        "http://www.esma.europa.eu/xbrl/role/all/ias_1_role-220000",
    }

    INCOME_STATEMENT: set[str] = {
        "http://www.esma.europa.eu/xbrl/role/all/ias_1_role-310000",
        "http://www.esma.europa.eu/xbrl/role/all/ias_1_role-320000",
    }
    CASH_FLOW: set[str] = {
        "http://www.esma.europa.eu/xbrl/role/all/ias_7_role-510000",
        "http://www.esma.europa.eu/xbrl/role/all/ias_7_role-520000",
    }

    CHANGES_EQUITY: set[str] = {
        "http://www.esma.europa.eu/xbrl/role/all/ias_1_role-610000"
        "http://www.esma.europa.eu/xbrl/role/all/ias_1_role-710000"
    }


class UpdateStatementDefinitionJson:
    """Load link roles into static data."""

    PATH_LINK_ROLE_XML_2020 = os.path.join(
        PATH_STATIC,
        "taxonomy_2020-03-16",
        "www.esma.europa.eu",
        "taxonomy",
        "2020-03-16",
        "esef_all-cal.xml",
    )
    PATH_LINK_ROLE_XML_2021 = os.path.join(
        PATH_STATIC,
        "taxonomy_2021-03-24",
        "www.esma.europa.eu",
        "taxonomy",
        "2021-03-24",
        "esef_all-cal.xml",
    )
    PATH_LINK_ROLE_XML_2022 = os.path.join(
        PATH_STATIC,
        "taxonomy_2022-03-24",
        "www.esma.europa.eu",
        "taxonomy",
        "2022-03-24",
        "esef_all-cal.xml",
    )
    PATH_JSON_MAP_FILE = os.path.join(
        PATH_PROJECT_ROOT,
        "pyesef",
        "static",
        "statement_definition.json",
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
    def base_taxonomy_2020(self) -> ModelXbrl:
        """Return the base taxonomy model XBRL for 2020."""
        return load_model_xbrl(
            zip_file_path=self.PATH_LINK_ROLE_XML_2020, cntlr=self.cntlr
        )

    @cached_property
    def base_taxonomy_2021(self) -> ModelXbrl:
        """Return the base taxonomy model XBRL for 2021."""
        return load_model_xbrl(
            zip_file_path=self.PATH_LINK_ROLE_XML_2021, cntlr=self.cntlr
        )

    @cached_property
    def base_taxonomy_2022(self) -> ModelXbrl:
        """Return the base taxonomy model XBRL for 2022."""
        return load_model_xbrl(
            zip_file_path=self.PATH_LINK_ROLE_XML_2022, cntlr=self.cntlr
        )

    def _loop_rel_set(
        self, link_role_definition: str, model_base_taxonomy: ModelXbrl
    ) -> set[str]:
        """Loop through relationship set."""
        base_taxonomy_rels = model_base_taxonomy.relationshipSet(
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
        data_set = set()

        for taxonomy in [
            self.base_taxonomy_2020,
            self.base_taxonomy_2021,
            self.base_taxonomy_2022,
        ]:
            for definition in LinkRoleDefinition.CASH_FLOW:
                data_set.update(
                    self._loop_rel_set(
                        link_role_definition=definition,
                        model_base_taxonomy=taxonomy,
                    )
                )

        self.output_data_dict[StatementName.CASH_FLOW.value] = list(data_set)

    def load_balance_sheet(self) -> None:
        """Load all balance sheet items."""
        data_set = set()

        for taxonomy in [self.base_taxonomy_2020, self.base_taxonomy_2021]:
            for definition in LinkRoleDefinition.BALANCE_SHEET:
                additional_set = self._loop_rel_set(
                    link_role_definition=definition,
                    model_base_taxonomy=taxonomy,
                )
                data_set.update(additional_set)

        self.output_data_dict[StatementName.BALANCE_SHEET.value] = list(data_set)

    def load_income_statement(self) -> None:
        """Load all income statement items."""
        data_set = set()

        for taxonomy in [self.base_taxonomy_2020, self.base_taxonomy_2021]:
            for definition in LinkRoleDefinition.INCOME_STATEMENT:
                data_set.update(
                    self._loop_rel_set(
                        link_role_definition=definition,
                        model_base_taxonomy=taxonomy,
                    )
                )

        self.output_data_dict[StatementName.INCOME_STATEMENT.value] = list(data_set)

    def load_changes_equity(self) -> None:
        """Load all changes in equity items."""
        data_set = set()

        for taxonomy in [self.base_taxonomy_2020, self.base_taxonomy_2021]:
            for definition in LinkRoleDefinition.CHANGES_EQUITY:
                data_set.update(
                    self._loop_rel_set(
                        link_role_definition=definition,
                        model_base_taxonomy=taxonomy,
                    )
                )

        self.output_data_dict[StatementName.CHANGES_EQUITY.value] = list(data_set)

    def save_dict_to_json(self) -> None:
        """Save data dict to JSON file."""
        with open(self.PATH_JSON_MAP_FILE, "w", encoding="UTF-8") as json_file:
            json.dump(self.output_data_dict, json_file)
