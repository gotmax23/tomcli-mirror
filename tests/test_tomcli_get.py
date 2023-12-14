# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: MIT

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from tomcli.cli.get import app


def test_get_basic_dump(writer: str, reader: str, test_data: Path):
    file = str(test_data / "pyproject.toml")
    args = [
        file,
        "build-system.build-backend",
        f"--writer={writer}",
        f"--reader={reader}",
    ]
    ran = CliRunner().invoke(app, args, catch_exceptions=False)
    expected = "hatchling.build\n"
    assert ran.exit_code == 0
    assert ran.stdout == expected


def test_get_invalid_selector(writer: str, reader: str, test_data: Path):
    file = str(test_data / "pyproject.toml")
    args = [
        file,
        "build-system.abc.xyz",
        f"--writer={writer}",
        f"--reader={reader}",
    ]
    ran = CliRunner().invoke(app, args)
    expected = (
        "Invalid selector 'build-system.abc.xyz': could not find 'build-system.abc'\n"
    )
    assert ran.exit_code == 1
    assert ran.stdout == expected


def test_get_dict_dump(writer: str, reader: str, test_data: Path):
    file = str(test_data / "pyproject.toml")
    args = [
        file,
        "build-system",
        f"--writer={writer}",
        f"--reader={reader}",
    ]
    ran = CliRunner().invoke(app, args)
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


def test_get_json_formatter(rwargs: list[str], test_data: Path) -> None:
    file = str(test_data / "pyproject.toml")
    args = [*rwargs, "-F", "json", file, "tool.hatch.version"]
    expected = '{"path": "src/tomcli/__init__.py"}\n'
    ran = CliRunner().invoke(app, args)
    assert ran.exit_code == 0
    assert ran.stdout == expected


def test_get_version():
    from tomcli import __version__ as ver

    ran = CliRunner().invoke(app, ["--version"])
    assert ran.exit_code == 0
    assert ran.stdout == ver + "\n"


def test_get_with_dots(rwargs: list[str], test_data: Path) -> None:
    file = str(test_data / "pyproject.toml")
    args = [
        *rwargs,
        "-F",
        "default",
        file,
        'project.entry-points."tomcli.formatters".default',
    ]
    expected = "tomcli.formatters.builtin:default_formatter\n"
    ran = CliRunner().invoke(app, args)
    assert ran.exit_code == 0
    assert ran.stdout == expected
