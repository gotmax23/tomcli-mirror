# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Optional

import typer

from . import formatters
from . import get as get_cmd
from . import set as set_cmd
from ._util import version_cb

APP = typer.Typer(context_settings=dict(help_option_names=["-h", "--help"]))
APP.command("get")(get_cmd.get)
APP.add_typer(set_cmd.app, name="set")
APP.command("formatters")(formatters.list_formatters)


@APP.callback()
def callback(
    _: Optional[bool] = typer.Option(
        None, "--version", is_eager=True, callback=version_cb
    ),
):
    pass
