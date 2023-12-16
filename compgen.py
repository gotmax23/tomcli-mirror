# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: MIT

"""
Generate completions for the Fedora RPM package. Not for public use.
"""

from __future__ import annotations

import os
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import click

_path_type = click.Path(path_type=Path)

COMMANDS = ("tomcli", "tomcli-get", "tomcli-set")


def get_complete_envvar(command: str) -> str:
    COMMAND = command.upper().replace("-", "_")
    return f"_{COMMAND}_COMPLETE"


@dataclass(frozen=True)
class Shell:
    name: str
    click_type: str
    get_path: Callable[[Path, str], Path]


BASH = Shell("bash", "bash_source", lambda path, name: path / name)
FISH = Shell("fish", "fish_source", lambda path, name: path / f"{name}.fish")
ZSH = Shell("zsh", "zsh_source", lambda path, name: path / f"_{name}")


def _get_shells_dict(
    installroot: Path, _shells: dict[Shell, Path | None]
) -> dict[Shell, Path]:
    shells: dict[Shell, Path] = {}
    for shell, directory in _shells.items():
        if not directory:
            continue
        directory = installroot / directory.resolve().relative_to("/")
        directory.mkdir(parents=True, exist_ok=True)
        shells[shell] = directory
    return shells


@click.command()
@click.option("--bash-dir", type=_path_type)
@click.option("--fish-dir", type=_path_type)
@click.option("--zsh-dir", type=_path_type)
@click.option("--installroot", type=_path_type, default=Path("/"))
def main(
    bash_dir: Path | None,
    fish_dir: Path | None,
    zsh_dir: Path | None,
    installroot: Path,
):
    _shells = {BASH: bash_dir, FISH: fish_dir, ZSH: zsh_dir}
    shells = _get_shells_dict(installroot, _shells)

    for command in COMMANDS:
        envvar = get_complete_envvar(command)
        click.secho(f"Installing {command} completions")
        for shell, directory in shells.items():
            click.secho(f"   * Installing completions for {shell.name}")
            dest = shell.get_path(directory, command)
            out: bytes = subprocess.run(
                [command],
                env=os.environ | {envvar: shell.click_type},
                check=True,
                capture_output=True,
            ).stdout
            dest.write_bytes(out)


if __name__ == "__main__":
    main()
