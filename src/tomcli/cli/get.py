# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
#
# SPDX-License-Identifier: MIT

# ruff: noqa: UP007

from __future__ import annotations

import sys
from collections.abc import Mapping, MutableMapping
from typing import Any, Optional

from typer import Argument, Typer

from tomcli.cli._util import _std_cm
from tomcli.toml import Reader, Writer, dump, load

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
        sys.exit(msg)
    return cur


@app.command()
def get(
    path: str = Argument(...),
    selector: str = Argument("."),
    reader: Optional[Reader] = None,
    writer: Optional[Writer] = None,
):
    # Allow fallback if options are not passed
    allow_fallback_r = not bool(reader)
    allow_fallback_w = not bool(writer)
    reader = reader or Reader.TOMLKIT
    writer = writer or Writer.TOMLKIT
    with _std_cm(path, sys.stdin.buffer, "rb") as fp:
        data = load(fp, reader, allow_fallback_r)
    selected = get_part(data, selector)
    if isinstance(selected, Mapping):
        dump(selected, sys.stdout.buffer, writer, allow_fallback_w)
    else:
        print(selected)
