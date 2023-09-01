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


def test_set_str_root(rwargs, tmp_path: Path):
    path = tmp_path / "pyproject.toml"
    copy2(TEST_DATA / "pyproject.toml", path)
    args = [*rwargs, str(path), "str", ".", "abc"]
    ran = CliRunner().invoke(app, args, catch_exceptions=False)
    assert ran.exit_code == 1
    fun_msg = (
        "Your heart is in the right place,"
        " but we can't replace the whole file with a string\n"
    )
    assert ran.stdout == fun_msg


def test_set_append(rwargs, tmp_path: Path):
    orig_path = TEST_DATA / "test2.toml"
    path = tmp_path / "test2.toml"
    orig = loads(orig_path.read_text())
    copy2(orig_path, path)

    args = [*rwargs, str(path), "append", "lst.data", "4"]
    ran = CliRunner().invoke(app, args, catch_exceptions=False)
    assert ran.exit_code == 0

    orig["lst"]["data"].append("4")
    assert loads(path.read_text()) == orig


def test_set_append_error(rwargs, tmp_path: Path):
    orig_path = TEST_DATA / "test2.toml"
    path = tmp_path / "test2.toml"
    copy2(orig_path, path)

    args = [*rwargs, str(path), "append", "abc.data", "4"]
    ran = CliRunner().invoke(app, args, catch_exceptions=False)
    assert ran.exit_code == 1
    assert ran.stdout == (
        "You can only append values to an existing list."
        " Use the 'list' subcommand to create a new list\n"
    )


def test_set_lists_replace_regex(rwargs, tmp_path: Path):
    orig_path = TEST_DATA / "test2.toml"
    path = tmp_path / "test2.toml"
    orig = loads(orig_path.read_text())
    copy2(orig_path, path)

    args = [*rwargs, str(path), "lists", "replace", "lst.data", r"\d", "xxxx"]
    ran = CliRunner().invoke(app, args, catch_exceptions=False)
    assert ran.exit_code == 0

    orig["lst"]["data"] = ["xxxx", "xxxx", "abc", "456"]
    assert loads(path.read_text()) == orig


def test_set_lists_replace_regex2(rwargs, tmp_path: Path):
    orig_path = TEST_DATA / "test2.toml"
    path = tmp_path / "test2.toml"
    orig = loads(orig_path.read_text())
    copy2(orig_path, path)

    args = [
        *rwargs,
        str(path),
        "lists",
        "replace",
        "--type=fnmatch",
        "mixed.data",
        "*",
        "xxxx",
    ]
    ran = CliRunner().invoke(app, args, catch_exceptions=False)
    assert ran.exit_code == 0

    orig["mixed"]["data"] = ["xxxx", 1, "xxxx", 2, "xxxx"]
    assert loads(path.read_text()) == orig


def test_set_lists_replace_regex_first(rwargs, tmp_path: Path):
    orig_path = TEST_DATA / "test2.toml"
    path = tmp_path / "test2.toml"
    orig = loads(orig_path.read_text())
    copy2(orig_path, path)

    args = [
        *rwargs,
        str(path),
        "lists",
        "replace",
        "--first",
        "lst.data",
        r"\d",
        "xxxx",
    ]
    ran = CliRunner().invoke(app, args, catch_exceptions=False)
    assert ran.exit_code == 0

    orig["lst"]["data"] = ["xxxx", "2", "abc", "456"]
    assert loads(path.read_text()) == orig


def test_lists_replace_error(rwargs, tmp_path: Path):
    orig_path = TEST_DATA / "test2.toml"
    path = tmp_path / "test2.toml"
    copy2(orig_path, path)

    args = [*rwargs, str(path), "lists", "replace", "abc.data", "xxx", "xxx"]
    ran = CliRunner().invoke(app, args, catch_exceptions=False)
    assert ran.exit_code == 1
    assert ran.stdout == "You cannot replace values unless the value is a list\n"
