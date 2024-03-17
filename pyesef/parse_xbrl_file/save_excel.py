"""Save to Excel."""

from __future__ import annotations

from enum import StrEnum
import logging
import os
from typing import TYPE_CHECKING

from openpyxl import Workbook
from openpyxl.styles import NamedStyle
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet
import pandas as pd
from pandas import ExcelWriter

from pyesef.const import PATH_PROJECT_ROOT

if TYPE_CHECKING:
    from pyesef.parse_xbrl_file.read_and_save_filings import ReadFiling


class DataSheetName(StrEnum):
    """Represent data sheet names."""

    DATA = "Data"
    DEFINITIONS = "Definitions"


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
        self.workbook: Workbook | None = None

        if df_to_save.empty:
            self.parent.cntlr.addToLog(
                "Empty output dataframe. Output file not saved.", level=logging.WARNING
            )
            return

        self.save()

    @property
    def _file_exists(self) -> bool:
        """Check if file exists."""
        return os.path.exists(self.TEMPLATE_OUTPUT_PATH_EXCEL)

    def save_definitions(self, writer: ExcelWriter) -> None:
        """Save definitions sheet."""
        if (
            not self.parent.definitions.empty
            and DataSheetName.DEFINITIONS.value not in writer.sheets
        ):
            self.parent.definitions.to_excel(
                writer,
                index=False,
                sheet_name=DataSheetName.DEFINITIONS.value,
                freeze_panes=(1, 0),
            )

    def save(self) -> None:
        """Save file."""
        with pd.ExcelWriter(
            self.TEMPLATE_OUTPUT_PATH_EXCEL,
            engine="openpyxl",
        ) as writer:
            self.df_to_save.to_excel(
                writer,
                index=False,
                sheet_name=DataSheetName.DATA.value,
                freeze_panes=(1, 0),
            )

            # Get the workbook and sheet objects
            worksheet: Worksheet = writer.sheets[DataSheetName.DATA.value]

            self._add_data_auto_filter(worksheet=worksheet)
            self._add_data_sheet_styling(worksheet=worksheet)
            self.save_definitions(writer=writer)

    def _add_data_auto_filter(self, worksheet: Worksheet) -> None:
        """Add auto filter to data sheet."""
        worksheet.auto_filter.ref = (  # Enable autofilter
            "A1:" + get_column_letter(worksheet.max_column) + str(worksheet.max_row)
        )

    def _add_data_sheet_styling(self, worksheet: Worksheet) -> None:
        """Add styling to data sheet."""
        date_style = NamedStyle(
            name="date_style"
        )  # Define a named style with the desired date format
        date_style.number_format = "yyyy-mm-dd"

        # Apply the date style to the entire column
        for cell in worksheet["A"]:
            cell.style = date_style

        # Define a named style for integer formatting
        int_style = NamedStyle(name="int_style")
        int_style.number_format = "0"

        # Apply the integer style to the value column (column 'B')
        for cell in worksheet["G"]:
            cell.style = int_style
