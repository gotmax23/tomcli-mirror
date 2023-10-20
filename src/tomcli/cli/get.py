# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import sys
from collections.abc import MutableMapping
from typing import Any, Optional

from typer import Argument, Option, Typer

from tomcli.cli._util import _std_cm, fatal, version_cb
from tomcli.formatters import DEFAULT_FORMATTER, get_formatter
from tomcli.toml import Reader, Writer, load

app = Typer(context_settings=dict(help_option_names=["-h", "--help"]))


def get_part(data: MutableMapping[str, Any], selector: str) -> Any:
    if selector == ".":
        return data

    cur = data
    parts = selector.split(".")
    idx = 0
    try:
        for idx, part in enumerate(parts):  # noqa: B007
            cur = cur[part]
    except (IndexError, KeyError):
        up_to = ".".join(parts[: idx + 1])
        msg = f"Invalid selector {selector!r}: could not find {up_to!r}"
        fatal(msg)
    return cur


@app.command()
def get(
    path: str = Argument(...),
    selector: str = Argument("."),
    reader: Optional[Reader] = None,
    writer: Optional[Writer] = None,
    formatter: str = Option(DEFAULT_FORMATTER, "-F", "--formatter"),
    _: Optional[bool] = Option(None, "--version", is_eager=True, callback=version_cb),
):
    """
    Query a TOML file
    """
    # Allow fallback if options are not passed
    allow_fallback_r = not bool(reader)
    allow_fallback_w = not bool(writer)
    reader = reader or Reader.TOMLKIT
    writer = writer or Writer.TOMLKIT
    with _std_cm(path, sys.stdin.buffer, "rb") as fp:
        data = load(fp, reader, allow_fallback_r)
    selected = get_part(data, selector)
    try:
        formatter_obj = get_formatter(
            formatter,
            reader=reader,
            writer=writer,
            allow_fallback_r=allow_fallback_r,
            allow_fallback_w=allow_fallback_w,
        )
    except KeyError:
        fatal(formatter, "is not a valid formatter")
    print(formatter_obj(selected))
