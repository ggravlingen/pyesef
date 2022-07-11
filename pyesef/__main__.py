"""Main."""
import argparse

from pyesef import __version__
from pyesef.helpers.extract_filings import extract_filings
from pyesef.helpers.read_filings import read_filings
from pyesef.utils import to_dataframe

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Handle XBRL files.")
    parser.add_argument("--version", action="version", version=f"pyesef {__version__}")
    parser.add_argument(
        "--extract",
        "-x",
        action="store_true",
        help="Extract all zip-files in the archive-folder",
    )
    parser.add_argument(
        "--export",
        "-e",
        action="store_true",
        help="Export all filings data to csv",
    )

    parser.add_argument(
        "--command",
        dest="command",
    )

    org_args = parser.parse_args()

    if org_args.extract:
        extract_filings()

    if org_args.export:
        filings = read_filings(filter_year=2021)
        data_frame = to_dataframe(filings)

        data_frame.to_csv("output.csv", sep=";", index=False)
