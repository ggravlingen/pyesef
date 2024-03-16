"""Helper to extract definitions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast

from arelle.ModelDtsObject import ModelConcept
import pandas as pd

from pyesef.utils.data_management import asdict_with_properties


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


def extract_definitions_to_csv(concept: ModelConcept) -> pd.DataFrame:
    """Save item definitions to a text file."""
    definition_list: list[DefinitionData] = []

    id_objects: dict[str, ModelConcept] = concept.modelDocument.idObjects
    for key in id_objects:
        property_view = id_objects[key].propertyView

        definition = _get_definition(property_view=property_view)
        label = _get_label(property_view=property_view)
        label_xml = _get_label_xml(property_view=property_view)

        if label_xml is not None and (
            "Abstract" in label_xml or "Member" in label_xml or "Axis" in label_xml
        ):
            continue

        definition_list.append(
            DefinitionData(
                label_xml=label_xml,
                label=label,
                definition=definition,
            )
        )

    return pd.json_normalize(  # type: ignore[arg-type]
        asdict_with_properties(obj) for obj in definition_list
    )
