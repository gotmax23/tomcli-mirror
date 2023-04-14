# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

from pathlib import Path

import typer
import typer.testing

from tomcli.cli.get import app

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def test_get_basic_dump(writer: str, reader: str):
    file = str(ROOT / "pyproject.toml")
    args = [
        file,
        "build-system.build-backend",
        f"--writer={writer}",
        f"--reader={reader}",
    ]
    ran = typer.testing.CliRunner().invoke(app, args, catch_exceptions=False)
    expected = "hatchling.build\n"
    assert ran.exit_code == 0
    assert ran.stdout == expected


def test_get_invalid_selector(writer: str, reader: str):
    file = str(ROOT / "pyproject.toml")
    args = [
        file,
        "build-system.abc.xyz",
        f"--writer={writer}",
        f"--reader={reader}",
    ]
    ran = typer.testing.CliRunner().invoke(app, args)
    expected = (
        "Invalid selector 'build-system.abc.xyz': could not find 'build-system.abc'\n"
    )
    assert ran.exit_code == 1
    assert ran.stdout == expected


def test_get_dict_dump(writer: str, reader: str):
    file = str(ROOT / "pyproject.toml")
    args = [
        file,
        "build-system",
        f"--writer={writer}",
        f"--reader={reader}",
    ]
    ran = typer.testing.CliRunner().invoke(app, args)
    valid = [
        i.strip()
        for i in (
            """
requires = ["hatchling"]
build-backend = "hatchling.build"
""",
            """
requires = [
    "hatchling",
]
build-backend = "hatchling.build"
""",
        )
    ]
    assert ran.exit_code == 0
    assert ran.stdout.strip() in valid
