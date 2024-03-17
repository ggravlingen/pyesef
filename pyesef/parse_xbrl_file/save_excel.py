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
                "Empty output dataframe. Output file not saved.",
                level=logging.WARNING,
            )
            return

        self.main()

    def main(self) -> None:
        """Run program."""
        with pd.ExcelWriter(
            path=self.TEMPLATE_OUTPUT_PATH_EXCEL,
            engine="openpyxl",
            mode="a",
            if_sheet_exists="overlay",
            engine_kwargs={},
        ) as writer:
            self.save(writer=writer)

    def save(self, writer: ExcelWriter) -> None:
        """Save file."""
        reader = pd.read_excel(self.TEMPLATE_OUTPUT_PATH_EXCEL)
        self.df_to_save.to_excel(
            excel_writer=writer,
            index=False,
            sheet_name=DataSheetName.DATA.value,
            freeze_panes=(1, 0),
            startcol=0,
            startrow=reader.shape[0] + 1,
        )

        self._add_data_auto_filter(writer=writer)
        self._add_data_sheet_styling(writer=writer)
        self._save_definitions(writer=writer)

    def _add_data_auto_filter(self, writer: ExcelWriter) -> None:
        """Add auto filter to data sheet."""
        worksheet: Worksheet = writer.sheets[DataSheetName.DATA.value]

        worksheet.auto_filter.ref = (  # Enable autofilter
            "A1:" + get_column_letter(worksheet.max_column) + str(worksheet.max_row)
        )

    def get_named_style_names(self, writer: ExcelWriter) -> list[str]:
        """Return a list of named styles."""
        return [
            style.name for style in writer.book._named_styles  # type: ignore # pylint: disable=protected-access
        ]

    def _add_data_sheet_styling(self, writer: ExcelWriter) -> None:
        """Add styling to data sheet."""
        worksheet: Worksheet = writer.sheets[DataSheetName.DATA.value]

        named_styles = self.get_named_style_names(writer=writer)

        if "date_style" not in named_styles:
            date_style = NamedStyle(
                name="date_style"
            )  # Define a named style with the desired date format
            date_style.number_format = "yyyy-mm-dd"

            # Apply the date style to the entire column
            for cell in worksheet["A"]:
                cell.style = date_style

        if "int_style" not in named_styles:
            # Define a named style for integer formatting
            int_style = NamedStyle(name="int_style")
            int_style.number_format = "0"

            # Apply the integer style to the value column (column 'B')
            for cell in worksheet["G"]:
                cell.style = int_style

    def _save_definitions(self, writer: ExcelWriter) -> None:
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
