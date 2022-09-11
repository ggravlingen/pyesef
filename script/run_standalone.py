"""Script to run the library stand-alone."""

import os
import sys

folder = os.path.dirname(__file__)
sys.path.insert(0, os.path.normpath(f"{folder}/.."))

from pyesef.helpers.read_and_save_filings import read_and_save_filings

read_and_save_filings()
