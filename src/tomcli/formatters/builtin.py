# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: MIT

from __future__ import annotations

import datetime
import json
from collections.abc import Mapping, MutableSequence
from typing import Any, cast

from ..toml import Writer, dumps
from . import FormatterError


def default_formatter(obj: Any, writer: Writer, allow_fallback_w: bool) -> str:
    """
    Use the `toml` formatter if the object is a Mapping and fall back to
    `string`.
    """
    if isinstance(obj, Mapping):
        return toml_formatter(
            cast("Mapping[str, Any]", obj),
            writer=writer,
            allow_fallback_w=allow_fallback_w,
        )
    return string_formatter(obj)


def toml_formatter(
    obj: Mapping[str, Any], writer: Writer, allow_fallback_w: bool
) -> str:
    """
    Return the TOML mapping of the object
    """
    return dumps(obj, prefered_writer=writer, allow_fallback=allow_fallback_w).strip()


def string_formatter(obj: Any) -> str:
    """
    Print the Python str() representation of the object
    """
    return str(obj)


def json_formatter(obj: Any) -> str:
    """
    Return the JSON representation of the object
    """
    return json.dumps(obj)


def newline_list_formatter(obj: Any) -> str:
    """
    Return a newline separated list
    """
    if not isinstance(obj, MutableSequence):
        raise FormatterError("The object is not a list")
    obj = cast("MutableSequence[Any]", obj)
    items: list[str] = []
    allowed_types = (str, int, float, datetime.datetime)
    for item in obj:
        if not isinstance(item, allowed_types):
            raise FormatterError(
                f"{type(item)} cannot be represented by a newline-separated list"
            )
        items.append(str(item))
    return "\n".join(items)


def newline_keys_formatter(obj: Any) -> str:
    """
    Return a newline-separated list of Mapping keys
    """
    if not isinstance(obj, Mapping):  # pragma: no cover
        raise FormatterError("The object is not a Mapping")
    obj = cast("Mapping[str, Any]", obj)
    return newline_list_formatter(list(obj.keys()))


def newline_values_formatter(obj: Any) -> str:
    """
    Return a newline-separated list of Mapping values
    """
    if not isinstance(obj, Mapping):  # pragma: no cover
        raise FormatterError("The object is not a Mapping")
    obj = cast("Mapping[str, Any]", obj)
    return newline_list_formatter(list(obj.values()))
