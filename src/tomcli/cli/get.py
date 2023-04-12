# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
#
# SPDX-License-Identifier: MIT

# ruff: noqa: UP007

from __future__ import annotations

import sys
from collections.abc import Iterable, Mapping, MutableMapping
from contextlib import contextmanager
from typing import Any, BinaryIO, Optional

from typer import Argument, Exit, Typer

from tomcli.toml import Reader, Writer, dump, load

app = Typer()


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
        raise Exit(msg) from None
    return cur


@contextmanager
def _std_cm(path: str, dash_stream: str, mode: str) -> Iterable[BinaryIO]:
    if str(path) == "-":
        yield dash_stream
    else:
        with open(path, mode) as fp:
            yield fp


@app.command()
def get(
    path: str = Argument(...),
    selector: str = Argument("."),
    reader: Optional[Reader] = None,
    writer: Optional[Writer] = None,
):
    allow_fallback_r = bool(reader)
    allow_fallback_w = bool(writer)
    reader = reader or Reader.TOMLKIT
    writer = writer or Writer.TOMLKIT
    with _std_cm(path, sys.stdin.buffer, "rb") as fp:
        data = load(fp, reader, allow_fallback_r)
    selected = get_part(data, selector)
    if isinstance(selected, Mapping):
        dump(selected, sys.stdout.buffer, writer, allow_fallback_w)
    else:
        print(selected)
