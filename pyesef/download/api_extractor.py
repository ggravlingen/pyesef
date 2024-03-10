"""API management."""

from __future__ import annotations

import json
import math
from urllib import request

from pyesef.download.common import Country, Filing
from pyesef.log import LOGGER

# Loads 1000 items at a time
API_URL = "https://filings.xbrl.org/api/filings?page%5Bsize%5D=1000&page%5Bnumber%5D="


DEBUG_FILTER_LEI_LIST: list[str] = []


def api_to_filing_record_list() -> list[Filing]:
    """Load API data."""
    filing_list: list[Filing] = []
    hash_list: list[str] = []

    # Determine number of pages with data
    with request.urlopen(f"{API_URL}0") as url:
        data = json.loads(url.read().decode())
        max_page_no = math.ceil(data["meta"]["count"] / 30)

    page_no = 0

    while page_no < max_page_no:
        LOGGER.info(f"Working on page {page_no}")
        with request.urlopen(f"{API_URL}{page_no}") as url:
            data = json.loads(url.read().decode())

            # There is no more data, we can return here
            if len(data["data"]) == 0:
                LOGGER.info("No data, aborting")
                return filing_list

            for filing in data["data"]:

                attributes = filing["attributes"]
                country_iso_2 = attributes["country"]

                # Filter on the Nordics
                if country_iso_2 not in [
                    Country.DENMARK,
                    Country.FINLAND,
                    Country.ICELAND,
                    Country.NORWAY,
                    Country.SWEDEN,
                ]:
                    continue

                relationships = filing["relationships"]

                related_list = str(relationships["entity"]["links"]["related"]).split(
                    "/"
                )

                lei = related_list[-1]

                # Allow debugging by filtering on the LEI codes in DEBUG_FILTER_LEI_LIST
                if len(DEBUG_FILTER_LEI_LIST) > 0 and lei not in DEBUG_FILTER_LEI_LIST:
                    continue

                period_end = attributes["period_end"]

                hash_key = f"{lei}{period_end}"
                if hash_key not in hash_list:
                    filing_list.append(
                        Filing(
                            lei=lei,
                            country_iso_2=attributes["country"],
                            period_end=period_end,
                            package_url=attributes["package_url"],
                        )
                    )
                    hash_list.append(hash_key)

        page_no += 1

    return filing_list
