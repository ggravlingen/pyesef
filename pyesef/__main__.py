"""Main."""

import argparse

from pyesef import __version__
from pyesef.download import download_packages
from pyesef.parse_xbrl_file import ReadFiling, UpdateStatementDefinitionJson

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Handle XBRL files.")
    parser.add_argument("--version", action="version", version=f"pyesef {__version__}")
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
    parser.add_argument(
        "--update",
        "-u",
        action="store_true",
        help="Update statement definitions",
    )

    org_args = parser.parse_args()

    if org_args.download:
        download_packages()

    if org_args.export:
        ReadFiling(should_move_parsed_file=False)

    if org_args.update:
        UpdateStatementDefinitionJson()
