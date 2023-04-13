# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

from pathlib import Path
from shutil import copy2

import typer.testing

from tomcli.cli.set import app
from tomcli.toml import load, loads

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def test_set_del(reader: str, writer: str) -> None:
    path = str(ROOT / "pyproject.toml")
    with open(path, "rb") as fp:
        data = load(fp)
    del data["build-system"]

    args = [
        "-o",
        "-",
        "--reader",
        reader,
        "--writer",
        writer,
        path,
        "del",
        "build-system",
    ]
    ran = typer.testing.CliRunner().invoke(app, args, catch_exceptions=False)
    assert ran.exit_code == 0
    assert loads(ran.stdout) == data


def test_set_del_inplace(reader: str, writer: str, tmp_path: Path) -> None:
    path = tmp_path / "pyproject.toml"
    copy2(ROOT / "pyproject.toml", path)
    with open(path, "rb") as fp:
        data = load(fp)
    del data["project"]["name"]

    args = ["--reader", reader, "--writer", writer, str(path), "del", "project.name"]
    ran = typer.testing.CliRunner().invoke(app, args, catch_exceptions=False)
    assert ran.exit_code == 0
    with open(path, "rb") as fp:
        assert data == load(fp)
