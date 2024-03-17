"""Save to Excel."""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

from openpyxl.styles import NamedStyle
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet
import pandas as pd

from pyesef.const import PATH_PROJECT_ROOT

if TYPE_CHECKING:
    from pyesef.parse_xbrl_file.read_and_save_filings import ReadFiling


class SaveToExcel:
    """
    Class to save data to Excel.

    Appends the data if the file exists.
    """

    TEMPLATE_OUTPUT_PATH_EXCEL = os.path.join(PATH_PROJECT_ROOT, "output.xlsx")

    def __init__(self, parent: ReadFiling, df_to_save: pd.DataFrame) -> None:
        """Init class."""
        self.parent = parent
        self.df_to_save = df_to_save

        if df_to_save.empty:
            self.parent.cntlr.addToLog(
                "Empty output dataframe. Output file not saved.", level=logging.WARNING
            )
            return

        self.save()

    def save(self) -> None:
        """Save file."""
        with pd.ExcelWriter(
            self.TEMPLATE_OUTPUT_PATH_EXCEL,
            engine="openpyxl",
        ) as writer:
            self.df_to_save.to_excel(
                writer,
                index=False,
                sheet_name="Data",
                freeze_panes=(1, 0),
            )

            # Define a named style with the desired date format
            date_style = NamedStyle(name="date_style")
            date_style.number_format = "yyyy-mm-dd"

            # Get the workbook and sheet objects
            worksheet: Worksheet = writer.sheets["Data"]

            # Enable autofilter
            worksheet.auto_filter.ref = (
                "A1:" + get_column_letter(worksheet.max_column) + str(worksheet.max_row)
            )

            # Apply the date style to the entire column
            for cell in worksheet["A"]:
                cell.style = date_style

            # Define a named style for integer formatting
            int_style = NamedStyle(name="int_style")
            int_style.number_format = "0"

            # Apply the integer style to the value column (column 'B')
            for cell in worksheet["G"]:
                cell.style = int_style

            # Store the definitions in the Excel file
            if not self.parent.definitions.empty:
                self.parent.definitions.to_excel(
                    writer,
                    index=False,
                    sheet_name="Definitions",
                    freeze_panes=(1, 0),
                )
