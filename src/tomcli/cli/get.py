# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import sys
from collections.abc import MutableMapping
from typing import Any

import click

from tomcli.cli._util import (
    DEFAULT_CONTEXT_SETTINGS,
    SELECTOR_HELP,
    SHARED_PARAMS,
    SharedArg,
    _std_cm,
    add_args_and_help,
    fatal,
    split_by_dot,
)
from tomcli.formatters import FormatterError, get_formatter
from tomcli.toml import Reader, Writer, load


def get_part(data: MutableMapping[str, Any], selector: str) -> Any:
    if selector == ".":
        return data

    cur = data
    parts = list(split_by_dot(selector))
    idx = 0
    try:
        for idx, part in enumerate(parts):  # noqa: B007
            cur = cur[part]
    except (IndexError, KeyError):
        up_to = ".".join(parts[: idx + 1])
        msg = f"Invalid selector {selector!r}: could not find {up_to!r}"
        fatal(msg)
    return cur


@click.command(name="get", context_settings=DEFAULT_CONTEXT_SETTINGS)
@SHARED_PARAMS.version
@SHARED_PARAMS.writer
@SHARED_PARAMS.reader
@SHARED_PARAMS.formatter
@add_args_and_help(
    SHARED_PARAMS.path,
    SharedArg(click.argument("selector", default="."), help=SELECTOR_HELP),
)
def get(
    path: str,
    selector: str,
    reader: Reader | None,
    writer: Writer | None,
    formatter: str,
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
    try:
        print(formatter_obj(selected))
    except FormatterError as exc:
        fatal(f"{formatter!r} formatter error:", exc)


app = get
