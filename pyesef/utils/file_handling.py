"""File handling utils."""

from __future__ import annotations

import os
from typing import cast

import jstyleson

from pyesef.const import PATH_BASE


def read_json(filename: str) -> dict[str, str]:
    """Open and read a json-file and return as a dict."""
    with open(os.path.join(PATH_BASE, filename), "rb") as _file:
        contents = _file.read()
        return cast(dict[str, str], jstyleson.loads(contents))
