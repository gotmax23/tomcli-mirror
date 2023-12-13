# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: MIT

from __future__ import annotations

import datetime
import json
from collections.abc import Mapping, MutableSequence
from typing import Any

from ..toml import Writer, dumps
from . import FormatterError


def default_formatter(obj, writer: Writer, allow_fallback_w: bool) -> str:
    """
    Use the `toml` formatter if the object is a Mapping and fall back to
    `string`.
    """
    if isinstance(obj, Mapping):
        return toml_formatter(obj, writer=writer, allow_fallback_w=allow_fallback_w)
    return string_formatter(obj)


def toml_formatter(
    obj: Mapping[str, Any], writer: Writer, allow_fallback_w: bool
) -> str:
    """
    Return the TOML mapping of the object
    """
    return dumps(obj, prefered_writer=writer, allow_fallback=allow_fallback_w).strip()


def string_formatter(obj) -> str:
    """
    Print the Python str() representation of the object
    """
    return str(obj)


def json_formatter(obj) -> str:
    """
    Return the JSON representation of the object
    """
    return json.dumps(obj)


def newline_list_formatter(obj) -> str:
    """
    Return a newline separated list
    """
    if not isinstance(obj, MutableSequence):
        raise FormatterError("The object is not a list")
    items: list[str] = []
    allowed_types = (str, int, float, datetime.datetime)
    for item in obj:
        if not isinstance(item, allowed_types):
            raise FormatterError(
                f"{type(item)} cannot be represented by a newline-separated list"
            )
        items.append(str(item))
    return "\n".join(items)
