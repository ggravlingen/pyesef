"""Helper to read filings."""

from __future__ import annotations

import os
from pathlib import Path
import time

from arelle import FileSource as FileSourceFile, PluginManager
from arelle.Cntlr import Cntlr
from arelle.CntlrCmdLine import filesourceEntrypointFiles
from arelle.FileSource import FileSource
from arelle.ModelDtsObject import ModelRelationship
from arelle.ModelRelationshipSet import ModelRelationshipSet
from arelle.ModelValue import QName
from arelle.ModelXbrl import ModelXbrl
from arelle.XbrlConst import summationItem
import pandas as pd

from pyesef.const import PATH_FAILED, PATH_PARSED
from pyesef.load_parse_file.common import EsefData
from pyesef.utils.data_management import asdict_with_properties

from ..const import CSV_SEPARATOR, FILE_ENDING_ZIP, PATH_ARCHIVES
from ..error import PyEsefError
from ..load_parse_file.read_facts import facts_to_data_list
from .hierarchy import Hierarchy


def data_list_to_clean_df(data_list: list[EsefData]) -> pd.DataFrame:
    """Convert a list of filing data to a Pandas dataframe."""
    data_frame_from_data_class = pd.json_normalize(  # type: ignore[arg-type]
        asdict_with_properties(obj) for obj in data_list
    )

    if data_frame_from_data_class.empty:
        return pd.DataFrame()

    data_frame_from_data_class["period_end"] = pd.to_datetime(
        data_frame_from_data_class["period_end"]
    )

    # Drop beginning-of-year items
    data_frame_from_data_class = data_frame_from_data_class.query(
        "not (period_end.dt.month == 1 & period_end.dt.day == 1)"
    )

    # Drop items before 2020
    data_frame_from_data_class = data_frame_from_data_class.query(
        "period_end.dt.year > 2020"
    )

    # Drop zero values
    data_frame_from_data_class = data_frame_from_data_class.query("value != 0")

    # It's easier to look for duplicates when using ints than when using floats
    try:
        data_frame_from_data_class["value_int"] = (
            data_frame_from_data_class["value"] * 100
        ).astype(int)
    except OverflowError:
        data_frame_from_data_class["value_int"] = (
            data_frame_from_data_class["value"]
        ).astype(int)

    # Drop any duplicates
    data_frame_no_duplicates = data_frame_from_data_class.drop_duplicates(
        subset=[
            "period_end",
            "lei",
            "wider_anchor_or_xml_name",
            "xml_name",
            "level_1",
            "value",
        ],
        ignore_index=True,
    )

    data_frame_no_duplicates = data_frame_no_duplicates.drop(columns=["value_int"])

    return data_frame_no_duplicates


class Controller(Cntlr):  # type: ignore
    """Controller."""

    def __init__(self) -> None:
        """Init controller with logging."""
        super().__init__(logFileName="logToPrint", hasGui=False)


def _load_esef_xbrl_model(zip_file_path: str, cntlr: Controller) -> ModelXbrl:
    """Load a ModelXbrl from a file path."""
    try:
        file_source: FileSource = FileSourceFile.openFileSource(
            zip_file_path,
            cntlr,
            checkIfXmlIsEis=False,
        )

        # Find entrypoint files
        _entrypoint_files = filesourceEntrypointFiles(
            filesource=file_source,
            entrypointFiles=[{"file": zip_file_path}],
        )

        # This is required to correctly populate _entrypointFiles
        for plugin_xbrl_method in PluginManager.pluginClassMethods(
            "CntlrCmdLine.Filing.Start"
        ):
            plugin_xbrl_method(
                cntlr,
                None,
                file_source,
                _entrypoint_files,
                sourceZipStream=None,
                responseZipStream=None,
            )
        _entrypoint = _entrypoint_files[0]
        _entrypoint_file = _entrypoint["file"]
        file_source.select(_entrypoint_file)
        cntlr.entrypointFile = _entrypoint_file

        # Load plugin
        cntlr.modelManager.validateDisclosureSystem = True
        cntlr.modelManager.disclosureSystem.select("esef")

        model_xbrl = cntlr.modelManager.load(
            file_source,
            "Loading",
            entrypoint=_entrypoint,
        )

        file_source.close()

        return model_xbrl
    except Exception as exc:
        raise OSError("File not loaded due to ", exc) from exc


def _clean_linkrole(link_role: str) -> str:
    """Clean link role."""
    split_link_role = link_role.split("/")
    return split_link_role[-1]


def _extract_model_roles(
    model_xbrl: ModelXbrl,
) -> tuple[dict[str, str], Hierarchy]:
    """
    Extract a lookup table between XML item name and the item's role.

    This allows us to determine what financial statement an item belongs to, eg income
    statement, cash flow analysis or balance sheet.
    """
    to_model_to_linkrole_map: dict[str, str] = {}
    hierarchy_dict: dict[str, str] = {}

    rel_set: ModelRelationshipSet = model_xbrl.relationshipSet(summationItem)
    concepts_by_roles: dict[str, list[str]] = {}

    model_relationships: list[ModelRelationship] = rel_set.modelRelationships

    try:
        for rel in model_relationships:
            link = concepts_by_roles.get(rel.linkrole, [])

            from_clark_qname: QName = rel.fromModelObject.qname
            to_clark_qname: QName = rel.toModelObject.qname
            from_clark = from_clark_qname.clarkNotation
            to_clark = to_clark_qname.clarkNotation

            if to_clark_qname not in to_model_to_linkrole_map:
                to_model_to_linkrole_map[to_clark_qname.localName] = _clean_linkrole(
                    rel.linkrole
                )

            if "summation-item" in rel.arcrole:
                # Create a lookup table of the parent item of each statement item, eg
                # DepreciationAndAmortisationExpense is part of OperatingExpense
                hierarchy_dict[to_clark_qname.localName] = from_clark_qname.localName

            if from_clark not in link and from_clark is not None:
                link.append(from_clark)

            if to_clark not in link and to_clark is not None:
                link.append(to_clark)

            if rel.linkrole not in concepts_by_roles:
                concepts_by_roles[rel.linkrole] = link

    except Exception as exc:
        raise PyEsefError("Unable to load model roles due to ", exc) from exc

    hierarchy_data = Hierarchy(hierarchy_dict=hierarchy_dict)

    return to_model_to_linkrole_map, hierarchy_data


class ReadFiling:
    """Read and save filings."""

    TEMPLATE_OUTPUT_PATH = "output.csv"

    def __init__(
        self,
        filing_folder: str = PATH_ARCHIVES,
        should_move_parsed_file: bool = True,
    ) -> None:
        """Init class."""
        start_time = time.time()

        self.filing_folder = filing_folder
        self.file_to_parse_list: list[str] = []
        self.filing_list: list[EsefData] = []
        self.should_move_parsed_file = should_move_parsed_file

        self.cntlr = Controller()  # The Arelle controller

        # Add support for reading ESEF-files
        PluginManager.addPluginModule("validate/ESEF")

        self.find_files()
        self.parse_file_list()
        self.save_to_csv()

        # Close the controller
        self.cntlr.close()
        end_time = time.time()
        total_time = round(end_time - start_time, 0)
        self.cntlr.addToLog(
            f"Parsed {len(self.file_to_parse_list)} files in {total_time}s"
        )

    def find_files(self) -> None:
        """Loop through the archive folder and locate relevant files to parse."""
        for subdir, _, files in os.walk(PATH_ARCHIVES):
            for file in files:
                zip_file_path = subdir + os.sep + file

                if not zip_file_path.endswith(FILE_ENDING_ZIP):
                    continue

                self.file_to_parse_list.append(zip_file_path)

    def parse_file_list(self) -> None:
        """PARSE FILE."""
        for zip_file_path in self.file_to_parse_list:
            try:
                # Load zip-file into a ModelXbrl instance
                model_xbrl: ModelXbrl = _load_esef_xbrl_model(
                    zip_file_path=zip_file_path,
                    cntlr=self.cntlr,
                )

                # Extract the model roles
                to_model_to_linkrole_map, _ = _extract_model_roles(
                    model_xbrl=model_xbrl,
                )

                fact_list = facts_to_data_list(
                    model_xbrl=model_xbrl,
                    to_model_to_linkrole_map=to_model_to_linkrole_map,
                )
                self.filing_list.extend(fact_list)
                model_xbrl.close()

                # Move the filing folder to another location.
                # This helps us if the script stops due to memory
                # constraints.
                if self.should_move_parsed_file:
                    self.move_parsed_file(
                        zip_file_path=zip_file_path, target_path=PATH_PARSED
                    )
                    self.cntlr.addToLog("Moved files to parsed folder")

            except Exception as exc:
                if self.should_move_parsed_file:
                    self.move_parsed_file(
                        zip_file_path=zip_file_path, target_path=PATH_FAILED
                    )
                    self.cntlr.addToLog(f"Moved file to error folder due to {exc}")

    def save_to_csv(self) -> None:
        """Save file to CSV."""
        data_frame_from_data_class = data_list_to_clean_df(self.filing_list)
        if data_frame_from_data_class.empty:
            return

        data_frame_from_data_class.to_csv(
            self.TEMPLATE_OUTPUT_PATH,
            sep=CSV_SEPARATOR,
            index=False,
            mode="a",
            header=not os.path.exists(self.TEMPLATE_OUTPUT_PATH),
        )

    @staticmethod
    def move_parsed_file(zip_file_path: str, target_path: str) -> None:
        """Move a file from the filings folder to the parsed folder."""
        Path(target_path).mkdir(parents=True, exist_ok=True)

        os.replace(
            zip_file_path,
            os.path.join(target_path, os.path.basename(zip_file_path)),
        )
