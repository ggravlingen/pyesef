"""Helper to read filings."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
import fractions
import os
import os.path
from typing import Any

from arelle import ModelManager, ModelXbrl
from arelle.ModelInstanceObject import ModelContext, ModelInlineFact

from ..const import PATH_FILINGS
from ..utils import Controller, parsed_value


@dataclass
class EsefData:
    """Represent ESEF data as a dataclass."""

    prefix: str
    local_name: str
    value: fractions.Fraction | int | Any | bool | str | None
    is_extension: bool = False


@dataclass
class FilingData:
    """Represent data for a filing."""

    lei: str
    period_end: date
    facts: list[EsefData]


def read_filings() -> list[EsefData]:
    """Read all filings in the filings folder."""
    cntlr = Controller()
    filing_list: list[FilingData] = []

    with os.scandir(PATH_FILINGS) as dir_iter:
        for entry in dir_iter:
            url_filing = ""
            url_taxonomy: list[str] = []

            for root, _, files in os.walk(entry.path):
                for file in files:
                    if (".xhtml") in file:
                        url_filing = os.path.join(root, file)

                    if "taxonomyPackage.xml" in file:
                        url_taxonomy.append(os.path.join(root, file))

                    if "catalog.xml" in file:
                        url_taxonomy.append(os.path.join(root, file))

            if url_filing != "" and url_taxonomy != "":
                try:
                    model_manager: ModelManager = ModelManager.initialize(cntlr)
                    model_xbrl: ModelXbrl = model_manager.load(
                        url_filing, taxonomyPackages=url_taxonomy
                    )
                    lei, period_end, facts = read_facts(model_xbrl)
                    filing_list.append(
                        FilingData(
                            lei=lei,
                            period_end=period_end,
                            facts=facts,
                        )
                    )
                    model_xbrl.close()
                except Exception as exc:
                    print(f"Error {entry.name} due to {exc}")

    return filing_list


def read_facts(modelXbrl: ModelXbrl) -> tuple(str, date, list[EsefData]):
    """Read facts."""
    fact_list: list[EsefData] = []

    for fact in modelXbrl.facts:
        assert isinstance(fact, ModelInlineFact)

        if fact.qname.prefix != "ifrs-full":
            is_extension = True
        else:
            is_extension = False

        if fact.qname.localName == "NameOfReportingEntityOrOtherMeansOfIdentification":
            context = fact.context
            assert isinstance(context, ModelContext)

            _, identifier = context.entityIdentifier

            date_period_end = (context.endDatetime - timedelta(days=1)).date()

            continue

        fact_list.append(
            EsefData(
                prefix=fact.qname.prefix,
                local_name=fact.qname.localName,
                value=parsed_value(fact),
                is_extension=is_extension,
            )
        )

    return identifier, date_period_end, fact_list
