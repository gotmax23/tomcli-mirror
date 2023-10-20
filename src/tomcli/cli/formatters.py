# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: MIT

from __future__ import annotations

import typer

from tomcli.formatters import get_formatters_list

from ._util import Annotated

APP = typer.Typer(context_settings=dict(help_option_names=["-h", "--help"]))


@APP.command()
def list_formatters(
    builtin_only: Annotated[
        bool, typer.Argument(help="Only list builtin formatters")
    ] = False
):
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
