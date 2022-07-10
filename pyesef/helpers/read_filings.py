"""Helper to read filings."""
from __future__ import annotations

import os

from arelle import ModelManager, ModelXbrl
from arelle.Cntlr import Cntlr

from ..const import PATH_FILINGS, FileName
from .read_facts import EsefData, read_facts


class Controller(Cntlr):  # type: ignore
    """Controller."""

    def __init__(self) -> None:
        """Init controller with logging."""
        super().__init__(logFileName="logToPrint")


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
                    if ".xhtml" in file:
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
                    fact_list = read_facts(
                        model_xbrl=model_xbrl,
                        filter_year=filter_year,
                    )
                    filing_list.extend(fact_list)
                    model_xbrl.close()
                except Exception as exc:
                    print(f"Error {entry.name} due to {exc}")

    return filing_list
