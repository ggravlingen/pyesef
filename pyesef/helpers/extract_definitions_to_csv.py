"""Helper to extract definitions."""
from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Any, cast

from arelle.ModelDtsObject import ModelConcept
import pandas as pd

from ..const import CSV_SEPARATOR
from ..utils import to_dataframe

DEFINITIONS_FILENAME = "definitions.csv"


@dataclass
class DefinitionData:
    """Definition of a statement item."""

    label_xml: str | None
    label: str | None
    definition: str | None


def _get_definition(property_view: tuple[str, Any]) -> str | None:
    for item in property_view:
        if item[0] == "label":
            try:
                return cast(str, item[2][0][1])
            except KeyError:
                return None

    return None


def _get_label(property_view: tuple[str, Any]) -> str | None:
    for item in property_view:
        if item and item[0] == "label":
            return cast(str, item[1])

    return None


def _get_label_xml(property_view: tuple[str, Any]) -> str | None:
    for item in property_view:
        if item[0] == "name":
            return cast(str, item[1])

    return None


def check_definitions_exists() -> bool:
    """Check if definitions file exists."""
    return os.path.isfile(DEFINITIONS_FILENAME)


def definitions_to_dict() -> dict[str, dict[str, str]]:
    """Create a lookup table of the definitions file."""
    data_frame = pd.read_csv(
        DEFINITIONS_FILENAME, sep=CSV_SEPARATOR, index_col="label_xml"
    )
    output_dict = data_frame.to_dict("index")
    return cast(dict[str, dict[str, str]], output_dict)


def extract_definitions_to_csv(concept: ModelConcept) -> None:
    """Save item definitions to a text file."""
    definition_list: list[DefinitionData] = []

    id_objects: dict[str, ModelConcept] = concept.modelDocument.idObjects
    for key in id_objects:
        property_view = id_objects[key].propertyView
        definition = _get_definition(property_view=property_view)
        label = _get_label(property_view=property_view)

        definition_list.append(
            DefinitionData(
                label_xml=_get_label_xml(property_view=property_view),
                label=label,
                definition=definition,
            )
        )

    data_frame = to_dataframe(definition_list)
    data_frame.to_csv(DEFINITIONS_FILENAME, sep=CSV_SEPARATOR, index=False)
