# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: MIT

from __future__ import annotations

import inspect
import sys
from collections.abc import Callable
from functools import lru_cache, partial
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

    from tomcli.toml import Reader, Writer

if sys.version_info >= (3, 11):
    import importlib.metadata as importlib_metadata
else:
    import importlib_metadata

FORMATTER_GROUP = "tomcli.formatters"
DEFAULT_FORMATTER = "default"


class FormatterError(Exception):
    """
    Error with formatting output
    """


FormatterType: TypeAlias = "Callable[..., str]"


@lru_cache
def get_formatters_list(
    builtin_only: bool = False,
) -> list[importlib_metadata.EntryPoint]:
    eps = importlib_metadata.entry_points(group=FORMATTER_GROUP)
    if builtin_only:
        eps = eps.select(module=f"{__package__}.builtin")
    return list(eps)


def get_formatters() -> dict[str, Callable[[], FormatterType]]:
    return {formatter.name: formatter.load for formatter in get_formatters_list()}


def get_formatter(
    name: str | None = None,
    *,
    reader: Reader,
    writer: Writer,
    allow_fallback_r: bool,
    allow_fallback_w: bool,
) -> FormatterType:
    name = name or DEFAULT_FORMATTER
    caller = get_formatters()[name]()
    sig = inspect.signature(caller)
    params: dict[str, Any] = {}
    for param_name in sig.parameters:
        if param_name == "reader":
            params["reader"] = reader
        elif param_name == "writer":
            params["writer"] = writer
        elif param_name == "allow_fallback_r":
            params["allow_fallback_r"] = allow_fallback_r
        elif param_name == "allow_fallback_w":
            params["allow_fallback_w"] = allow_fallback_w
    return partial(caller, **params)
