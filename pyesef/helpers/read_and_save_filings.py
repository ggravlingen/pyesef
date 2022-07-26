"""Helper to read filings."""
from __future__ import annotations

import os
import time
import traceback

from arelle import FileSource as FileSourceFile, PluginManager
from arelle.Cntlr import Cntlr
from arelle.CntlrCmdLine import filesourceEntrypointFiles
from arelle.FileSource import FileSource
from arelle.ModelValue import QName
from arelle.ModelXbrl import ModelXbrl
from arelle.XbrlConst import summationItem

from ..const import CSV_SEPARATOR, FILE_ENDING_ZIP, PATH_ARCHIVES
from ..error import PyEsefError
from ..utils import move_file_to_error, move_file_to_parsed, to_dataframe
from .read_facts import EsefData, read_facts


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
        raise IOError("File not loaded due to ", exc) from exc


def _extract_model_roles(model_xbrl: ModelXbrl) -> dict[str, str]:
    """
    Extract a lookup table between XML item name and the item's role.

    This allows us to determine what financial statement an item belongs to, eg income
    statement, cash flow analysis or balance sheet.
    """
    result_dict: dict[str, str] = {}

    rel_set = model_xbrl.relationshipSet(summationItem)
    concepts_by_roles: dict[str, list[str]] = {}

    try:
        for rel in rel_set.modelRelationships:
            link = concepts_by_roles.get(rel.linkrole, [])

            from_clark_qname: QName = rel.fromModelObject.qname
            to_clark_qname: QName = rel.toModelObject.qname
            from_clark = from_clark_qname.clarkNotation
            to_clark = to_clark_qname.clarkNotation

            if from_clark not in link and from_clark is not None:
                link.append(from_clark)

            if to_clark not in link and to_clark is not None:
                link.append(to_clark)

            if rel.linkrole not in concepts_by_roles:
                concepts_by_roles[rel.linkrole] = link

        for key, value_list in concepts_by_roles.items():
            for item in value_list:
                if item not in result_dict:
                    result_dict[item] = key.split("/")[-1]
    except Exception as exc:
        raise PyEsefError("Unable to load model roles due to ", exc) from exc

    return result_dict


def read_and_save_filings() -> None:
    """Read all filings in the filings folder."""
    idx = 0
    start = time.time()
    cntlr = Controller()
    PluginManager.addPluginModule("validate/ESEF")

    for subdir, _, files in os.walk(PATH_ARCHIVES):
        cntlr.addToLog(f"Parsing {len(files)} reports in folder {subdir}")

        for file in files:
            cntlr.addToLog(f"Working on file {file}")

            _error: bool = False
            error_message: str | None = None
            filing_list: list[EsefData] = []

            zip_file_path = subdir + os.sep + file

            if zip_file_path.endswith(FILE_ENDING_ZIP):
                try:
                    # Load zip-file into a ModelXbrl instance
                    model_xbrl: ModelXbrl = _load_esef_xbrl_model(
                        zip_file_path=zip_file_path,
                        cntlr=cntlr,
                    )

                    # Extract the model roles
                    model_roles = _extract_model_roles(
                        model_xbrl=model_xbrl,
                    )

                    # Read all facts into a list
                    try:
                        fact_list = read_facts(
                            model_xbrl=model_xbrl,
                            model_roles=model_roles,
                        )
                    except Exception as exc:
                        raise PyEsefError("Fact list error", exc) from exc
                    filing_list.extend(fact_list)
                    model_xbrl.close()
                except Exception as exc:
                    error_message = "".join(
                        traceback.TracebackException.from_exception(exc).format()
                    )
                    _error = True

                if _error and error_message is not None:
                    move_file_to_error(zip_file_path=zip_file_path)
                    cntlr.addToLog(f"Moved file to error folder due to {error_message}")
                else:
                    idx += 1
                    data_frame = to_dataframe(filing_list)
                    output_path = "output.csv"
                    data_frame.to_csv(
                        output_path,
                        sep=CSV_SEPARATOR,
                        index=False,
                        mode="a",
                        header=not os.path.exists(output_path),
                    )

                    # Move the filing folder to another location.
                    # This helps us if the script stops due to memory
                    # constraints.
                    move_file_to_parsed(zip_file_path=zip_file_path)
                    cntlr.addToLog("Moved files to parsed folder")

    end = time.time()
    total_time = end - start
    cntlr.addToLog(f"Loaded {idx} XBRL-files in {total_time}s")

    cntlr.addToLog("Finished loading")
    cntlr.close()
