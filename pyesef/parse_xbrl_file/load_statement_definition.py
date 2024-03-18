"""Based on https://gist.github.com/AustinMatherne/f9a101ff48298f5b97b26e7f6e28833b."""

from dataclasses import dataclass
import json
import os

from arelle import PluginManager
from arelle.ModelXbrl import ModelXbrl
from arelle.XbrlConst import parentChild
import requests

from pyesef.const import PATH_PROJECT_ROOT, PATH_STATIC
from pyesef.utils.file_handler import delete_folder, unzip_file

from .common import Controller, StatementName, load_model_xbrl


@dataclass
class TaxonomyFileData:
    """Define taxonomy file data."""

    zip_url: str
    folder_name: str
    folder_date: str

    @property
    def local_file_name(self) -> str:
        """Return file name."""
        split_zip_url = self.zip_url.split("/")
        return os.path.join(PATH_STATIC, split_zip_url[-1])

    @property
    def local_folder_path(self) -> str:
        """Return folder path."""
        return os.path.join(PATH_STATIC, self.folder_name)


TAXONOMY_URL_DATA = (
    TaxonomyFileData(
        zip_url="https://www.esma.europa.eu/sites/default/files/library/esef_taxonomy_2019.zip",
        folder_name="esef_taxonomy_2019",
        folder_date="2019-03-27",
    ),
    TaxonomyFileData(
        zip_url="https://www.esma.europa.eu/sites/default/files/library/esef_taxonomy_2020.zip",
        folder_name="esef_taxonomy_2020",
        folder_date="2020-03-16",
    ),
    TaxonomyFileData(
        zip_url="https://www.esma.europa.eu/sites/default/files/library/esef_taxonomy_2021.zip",
        folder_name="esef_taxonomy_2021",
        folder_date="2021-03-24",
    ),
)


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

    PATH_JSON_MAP_FILE = os.path.join(
        PATH_PROJECT_ROOT,
        "pyesef",
        "static",
        "statement_definition.json",
    )

    def __init__(self) -> None:
        """Init class."""
        self.output_data_dict: dict[str, list[str]] = {}
        self.list_xml_definition: list[str] = []
        self.xbrl_file_list: list[ModelXbrl] = []

        self.cntlr = Controller()

        # Add support for reading ESEF-files
        PluginManager.addPluginModule("validate/ESEF")

        self.main()

    def main(self) -> None:
        """Run sequence of methods."""
        self.download_unzip_zip_file()
        self.load_taxonomy_file()

        self.load_cashflow()
        self.load_balance_sheet()
        self.load_income_statement()
        self.load_changes_equity()
        self.save_dict_to_json()

        self.cleanup_files()

    def cleanup_files(self) -> None:
        """Delete files and folders."""
        for file_data in TAXONOMY_URL_DATA:
            delete_folder(file_data.local_folder_path)
            os.remove(file_data.local_file_name)

    def download_unzip_zip_file(self) -> None:
        """Download zip files."""
        for file_data in TAXONOMY_URL_DATA:
            req = requests.get(file_data.zip_url, stream=True, timeout=30)
            with open(file_data.local_file_name, "wb") as _file:
                for chunk in req.iter_content(chunk_size=2048):
                    _file.write(chunk)

            unzip_file(file_data.local_file_name, extract_to=PATH_STATIC)

            self.list_xml_definition.append(
                os.path.join(
                    PATH_STATIC,
                    file_data.folder_name,
                    "www.esma.europa.eu",
                    "taxonomy",
                    file_data.folder_date,
                    "esef_all-cal.xml",
                )
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

    def load_taxonomy_file(self) -> None:
        """Load taxonomy files."""
        for taxonomy_file in self.list_xml_definition:
            xbrl_taxonomy = load_model_xbrl(
                zip_file_path=taxonomy_file,
                cntlr=self.cntlr,
            )

            self.xbrl_file_list.append(xbrl_taxonomy)

    def load_cashflow(self) -> None:
        """Load all cash flow items."""
        data_set = set()

        for xbrl_taxonomy in self.xbrl_file_list:
            for definition in LinkRoleDefinition.CASH_FLOW:
                data_set.update(
                    self._loop_rel_set(
                        link_role_definition=definition,
                        model_base_taxonomy=xbrl_taxonomy,
                    )
                )

        sorted_list = sorted(data_set)
        self.output_data_dict[StatementName.CASH_FLOW.value] = sorted_list

    def load_balance_sheet(self) -> None:
        """Load all balance sheet items."""
        data_set = set()

        for xbrl_taxonomy in self.xbrl_file_list:
            for definition in LinkRoleDefinition.BALANCE_SHEET:
                additional_set = self._loop_rel_set(
                    link_role_definition=definition,
                    model_base_taxonomy=xbrl_taxonomy,
                )
                data_set.update(additional_set)

        sorted_list = sorted(data_set)
        self.output_data_dict[StatementName.BALANCE_SHEET.value] = sorted_list

    def load_income_statement(self) -> None:
        """Load all income statement items."""
        data_set = set()

        for xbrl_taxonomy in self.xbrl_file_list:
            for definition in LinkRoleDefinition.INCOME_STATEMENT:
                data_set.update(
                    self._loop_rel_set(
                        link_role_definition=definition,
                        model_base_taxonomy=xbrl_taxonomy,
                    )
                )

        sorted_list = sorted(data_set)
        self.output_data_dict[StatementName.INCOME_STATEMENT.value] = sorted_list

    def load_changes_equity(self) -> None:
        """Load all changes in equity items."""
        data_set = set()

        for xbrl_taxonomy in self.xbrl_file_list:
            for definition in LinkRoleDefinition.CHANGES_EQUITY:
                data_set.update(
                    self._loop_rel_set(
                        link_role_definition=definition,
                        model_base_taxonomy=xbrl_taxonomy,
                    )
                )

        sorted_list = sorted(data_set)
        self.output_data_dict[StatementName.CHANGES_EQUITY.value] = sorted_list

    def save_dict_to_json(self) -> None:
        """Save data dict to JSON file."""
        with open(self.PATH_JSON_MAP_FILE, "w", encoding="UTF-8") as json_file:
            json.dump(self.output_data_dict, json_file)
