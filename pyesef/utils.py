"""Utils."""
from __future__ import annotations

import fractions
from typing import Any

from arelle import Cntlr
from arelle.ModelDtsObject import ModelConcept
from arelle.ModelInstanceObject import ModelFact
from arelle.ModelValue import dateTime
from arelle.ValidateXbrlCalcs import roundValue


class Controller(Cntlr.Cntlr):
    """Controller."""

    def __init__(self):
        """Init controller with logging."""
        super().__init__(logFileName="logToPrint")


def parsed_value(
    fact: ModelFact,
) -> (fractions.Fraction | int | Any | bool | str | None):
    """Parse value."""
    if fact is None:
        return None
    concept = fact.concept  # type: ModelConcept
    if concept is None or concept.isTuple or fact.isNil:
        return None
    if concept.isFraction:
        num, den = map(fractions.Fraction, fact.fractionValue)
        return num / den
    val = fact.value.strip()
    if concept.isInteger:
        return int(val)
    elif concept.isNumeric:
        dec = fact.decimals
        if dec is None or dec == "INF":  # show using decimals or reported format
            dec = len(val.partition(".")[2])
        else:  # max decimals at 28
            dec = max(
                min(int(dec), 28), -28
            )  # 2.7 wants short int, 3.2 takes regular int, don't use _INT here
        num = roundValue(val, fact.precision, dec)  # round using reported decimals
        return num
    elif concept.baseXbrliType == "dateItemType":
        return dateTime(val)
    elif concept.baseXbrliType == "booleanItemType":
        return val.lower() in ("1", "true")
    elif concept.isTextBlock:
        return " ".join(val.split())
    return val
