"""Helper to read filings."""
from __future__ import annotations

import os

from arelle import ModelManager, ModelXbrl
from arelle.Cntlr import Cntlr
from arelle.XbrlConst import summationItem

from ..const import FILE_ENDING_XML, PATH_FILINGS, FileName
from .read_facts import EsefData, read_facts


class Controller(Cntlr):  # type: ignore
    """Controller."""

    def __init__(self) -> None:
        """Init controller with logging."""
        super().__init__(logFileName="logToPrint")


def extract_model_roles(model_xbrl: ModelXbrl) -> dict[str, str]:
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

        from_clark = rel.fromModelObject.qname.clarkNotation
        to_clark = rel.toModelObject.qname.clarkNotation

        if from_clark not in link:
            link.append(from_clark)

        if to_clark not in link:
            link.append(to_clark)

        if rel.linkrole not in concepts_by_roles:
            concepts_by_roles[rel.linkrole] = link

    for key, value_list in concepts_by_roles.items():
        for item in value_list:
            if item not in result_dict:
                result_dict[item] = key.split("/")[-1]

    return result_dict


def read_filings(filter_year: int | None = None) -> list[EsefData]:
    """Read all filings in the filings folder."""
    cntlr = Controller()
    filing_list: list[EsefData] = []

    with os.scandir(PATH_FILINGS) as dir_iter:
        for entry in dir_iter:
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

                    model_roles = extract_model_roles(model_xbrl=model_xbrl)

                    fact_list = read_facts(
                        model_xbrl=model_xbrl,
                        filter_year=filter_year,
                        model_roles=model_roles,
                    )
                    filing_list.extend(fact_list)
                    model_xbrl.close()
                except Exception as exc:
                    print(f"Error {entry.name} due to {exc}")

    return filing_list
