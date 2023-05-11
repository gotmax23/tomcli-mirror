# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

from pathlib import Path
from shutil import copy2

import pytest
from typer.testing import CliRunner

from tomcli.cli.set import app
from tomcli.toml import load, loads

HERE = Path(__file__).resolve().parent
TEST_DATA = HERE / "test_data"
ROOT = HERE.parent


def test_set_del(reader: str, writer: str) -> None:
    path = str(TEST_DATA / "pyproject.toml")
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
    ran = CliRunner().invoke(app, args, catch_exceptions=False)
    assert ran.exit_code == 0
    assert loads(ran.stdout) == data


def test_set_del_inplace(reader: str, writer: str, tmp_path: Path) -> None:
    path = tmp_path / "pyproject.toml"
    copy2(TEST_DATA / "pyproject.toml", path)
    with open(path, "rb") as fp:
        data = load(fp)
    del data["project"]["name"]

    args = ["--reader", reader, "--writer", writer, str(path), "del", "project.name"]
    ran = CliRunner().invoke(app, args, catch_exceptions=False)
    assert ran.exit_code == 0
    with open(path, "rb") as fp:
        assert data == load(fp)


@pytest.mark.parametrize(
    "typ, expected",
    [
        pytest.param("str", {"data": "3.14"}),
        pytest.param("float", {"data": 3.14}),
        pytest.param("int", {"data": 3}),
        pytest.param("list", {"data": ["3.14"]}),
    ],
)
def test_set(rwargs, typ: str, expected):
    path = TEST_DATA / "test1.toml"
    with open(path, "rb") as fp:
        data = load(fp)
    data.update(expected)

    args = [*rwargs, "-o", "-", str(path), typ, "data", "3.14"]
    ran = CliRunner().invoke(app, args, catch_exceptions=False)
    print(ran.stdout)
    assert ran.exit_code == 0
    assert loads(ran.stdout) == data


def test_set_multilevel(reader: str, writer: str, tmp_path: Path):
    path = tmp_path / "pyproject.toml"
    copy2(TEST_DATA / "pyproject.toml", path)
    with open(path, "rb") as fp:
        data = load(fp)
    # Replace project.license string with dict
    data["project"]["license"] = {"text": "MIT"}

    for cmd in (("del", "project.license"), ("str", "project.license.text", "MIT")):
        args = ["--reader", reader, "--writer", writer, str(path), *cmd]
        ran = CliRunner().invoke(app, args, catch_exceptions=False)
        assert ran.exit_code == 0
    with open(path, "rb") as fp:
        assert data == load(fp)
