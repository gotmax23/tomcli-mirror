# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: MIT

from __future__ import annotations

import click

from tomcli import __doc__ as _doc
from tomcli import __version__ as _ver

from . import formatters
from . import get as get_cmd
from . import set as set_cmd
from ._util import DEFAULT_CONTEXT_SETTINGS


@click.group(context_settings=DEFAULT_CONTEXT_SETTINGS, help=_doc)
@click.version_option(_ver, message="%(version)s")
def APP(): ...


APP.add_command(get_cmd.app)
APP.add_command(set_cmd.app)
APP.add_command(formatters.APP)
