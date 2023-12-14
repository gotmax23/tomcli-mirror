# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: MIT

from __future__ import annotations

from click.testing import CliRunner

from tomcli.cli.main import APP


def test_main_version():
    from tomcli import __version__ as ver

    ran = CliRunner().invoke(APP, ["--version"])
    assert ran.exit_code == 0
    assert ran.stdout == ver + "\n"


def test_formatters_list():
    ran = CliRunner().invoke(APP, ["formatters", "--builtin-only"])
    assert ran.exit_code == 0
    expected = """\
default
	Use the `toml` formatter if the object is a Mapping and fall back to
	`string`.

json
	Return the JSON representation of the object

newline-list
	Return a newline separated list

string
	Print the Python str() representation of the object

toml
	Return the TOML mapping of the object

"""
    assert ran.stdout == expected
