# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: MIT

from __future__ import annotations

import click

from tomcli.formatters import get_formatters_list

from ._util import DEFAULT_CONTEXT_SETTINGS, SHARED_PARAMS


@click.command(name="formatters", context_settings=DEFAULT_CONTEXT_SETTINGS)
@SHARED_PARAMS.version
@click.option(
    "--builtin-only / --no-builtin-only",
    default=False,
    help="Only list builtin formatters",
)
def list_formatters(builtin_only: bool):
    """
    List formatters for use tomcli-get
    """
    items: list[str] = []
    for obj in get_formatters_list(builtin_only):
        name = obj.name
        item = name + "\n"
        if docs := obj.load().__doc__:
            docs = "\n".join(
                "\t" + s for line in docs.splitlines() if (s := line.strip())
            )
            item += docs + "\n"
        items.append(item)
    print("\n".join(items))


APP = list_formatters
