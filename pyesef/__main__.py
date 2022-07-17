"""Main."""
import argparse

from pyesef import __version__
from pyesef.helpers.download_package import download_packages
from pyesef.helpers.extract_filings import extract_filings
from pyesef.helpers.read_and_save_filings import read_and_save_filings

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
        "--download",
        "-d",
        action="store_true",
        help="Download all packages from repository",
    )

    org_args = parser.parse_args()

    if org_args.download:
        download_packages()

    if org_args.extract:
        extract_filings()

    if org_args.export:
        read_and_save_filings()
