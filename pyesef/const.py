"""Constants."""

from __future__ import annotations

from enum import StrEnum
import os
import pathlib

PATH_BASE = pathlib.Path(__file__).parent.resolve()
PATH_PROJECT_ROOT = os.path.abspath(os.path.join(PATH_BASE, ".."))
PATH_STATIC = os.path.join(PATH_PROJECT_ROOT, "pyesef", "static")


class NiceType(StrEnum):
    """Representation of different types of 'nice types'."""

    PER_SHARE = "PerShare"
    SHARES = "Shares"
