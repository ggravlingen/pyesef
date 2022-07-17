"""Helper to read filings."""
from __future__ import annotations

import logging
import os
import time

from arelle import ModelManager
from arelle.Cntlr import Cntlr
from arelle.ModelValue import QName
from arelle.ModelXbrl import ModelXbrl
from arelle.XbrlConst import summationItem

from ..const import CSV_SEPARATOR, FILE_ENDING_XML, PATH_FILINGS, FileName
from ..utils import move_file_to_parsed, to_dataframe
from .read_facts import EsefData, read_facts


class Controller(Cntlr):  # type: ignore
    """Controller."""

    def __init__(self) -> None:
        """Init controller with logging."""
        super().__init__(logFileName="logToPrint")


def _extract_model_roles(model_xbrl: ModelXbrl) -> dict[str, str]:
    """
    Extract a lookup table between XML item name and the item's role.

    This allows us to determine what financial statement an item belongs to, eg income
    statement, cash flow analysis or balance sheet.
    """
    result_dict: dict[str, str] = {}

    rel_set = model_xbrl.relationshipSet(summationItem)
    concepts_by_roles: dict[str, list[str]] = {}

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

    return result_dict


def read_and_save_filings() -> None:
    """Read all filings in the filings folder."""
    idx = None
    start = time.time()
    cntlr = Controller()

    # Count the number of folders in the filings directory
    no_folders = len([1 for _ in list(os.scandir(PATH_FILINGS))])

    with os.scandir(PATH_FILINGS) as dir_iter:
        cntlr.addToLog(f"Parsing {no_folders} reports")
        for idx, entry in enumerate(dir_iter):
            filing_list: list[EsefData] = []
            url_filing: str | None = None
            url_taxonomy: list[str] = []

            for root, _, files in os.walk(entry.path):
                for file in files:
                    if FILE_ENDING_XML in file:
                        url_filing = os.path.join(root, file)

                    if file in [
                        FileName.TAXONOMY_PACKAGE,
                        FileName.TAXONOMY_PACKAGE_DOT,
                        FileName.CATALOG,
                    ]:
                        url_taxonomy.append(os.path.join(root, file))

            if url_filing is not None and url_taxonomy:
                try:
                    model_manager: ModelManager = ModelManager.initialize(cntlr)
                    model_xbrl: ModelXbrl = model_manager.load(
                        url_filing, taxonomyPackages=url_taxonomy
                    )

                    model_roles = _extract_model_roles(model_xbrl=model_xbrl)

                    fact_list = read_facts(
                        model_xbrl=model_xbrl,
                        model_roles=model_roles,
                    )
                    filing_list.extend(fact_list)
                    model_xbrl.close()
                except Exception as exc:
                    cntlr.addToLog(
                        f"Error {entry.name} due to {exc}",
                        level=logging.WARNING,
                    )

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
            move_file_to_parsed(entry=entry)
            cntlr.addToLog("Moved files to parsed folder")

    if idx is not None:
        end = time.time()
        total_time = end - start
        cntlr.addToLog(f"Loaded {idx+1} XBRL-files in {total_time}s")

    cntlr.addToLog("Finished loading")
    cntlr.close()
