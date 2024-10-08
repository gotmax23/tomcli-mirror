# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: MIT

from __future__ import annotations

import glob
import os
from collections.abc import Sequence
from glob import iglob
from pathlib import Path
from shutil import copy2
from typing import Any, Union

import nox

StrPath = Union[str, "os.PathLike[str]"]
IN_CI = "JOB_ID" in os.environ or "CI" in os.environ
ALLOW_EDITABLE = os.environ.get("ALLOW_EDITABLE", str(not IN_CI)).lower() in (
    "1",
    "true",
)

PROJECT = "tomcli"
SPECFILE = "tomcli.spec"
LINT_SESSIONS = ("formatters", "codeqa", "typing")
LINT_FILES = (
    f"src/{PROJECT}",
    "tests/",
    "noxfile.py",
    "compgen.py",
    "doc/mkdocs_mangen.py",
)
RELEASERR = "releaserr"

nox.options.sessions = (*LINT_SESSIONS, "covtest")


# Helpers


def install(session: nox.Session, *args: str, editable: bool = False, **kwargs: Any):
    if editable and ALLOW_EDITABLE:
        args = ("-e", *args)
    session.install(*args, **kwargs)


def git(session: nox.Session, *args: StrPath, **kwargs: Any):
    return session.run("git", *args, **kwargs, external=True)


# General


@nox.session(python=["3.9", "3.10", "3.11", "3.12", "3.13"])
def test(session: nox.Session):
    packages: list[str] = [".[all,tomli,test]"]
    env: dict[str, str] = {}
    tmp = Path(session.create_tmp())

    if any(i.startswith("--cov") for i in session.posargs):
        packages.extend(("coverage[toml]", "pytest-cov"))
        env["COVERAGE_FILE"] = str(tmp / ".coverage")

    install(session, *packages, editable=True)
    session.run(
        "pytest", "src", "tests", "--doctest-modules", *session.posargs, env=env
    )


@nox.session
def coverage(session: nox.Session):
    install(session, "coverage[toml]")
    session.run("coverage", "combine", "--keep", *iglob(".nox/test*/tmp/.coverage"))
    session.run("coverage", "html")
    session.run("coverage", "report", "--fail-under=95")


@nox.session()
def covtest(session: nox.Session):
    session.run("rm", "-f", *glob.iglob(".nox/*/tmp/.coverage*"), external=True)
    test_sessions = (f"test-{v}" for v in test.python)  # type: ignore[attr-defined]
    for target in test_sessions:
        session.notify(target, ["--cov"])
    session.notify("coverage")


@nox.session(venv_backend="none")
def lint(session: nox.Session):
    """
    Run formatters, codeqa, and typing sessions
    """
    for notify in LINT_SESSIONS:
        session.notify(notify)


@nox.session
def codeqa(session: nox.Session):
    install(session, ".[codeqa]")
    session.run("ruff", "check", *session.posargs, *LINT_FILES)
    session.run("reuse", "lint")


@nox.session
def formatters(session: nox.Session):
    install(session, ".[formatters]")
    posargs = session.posargs
    if IN_CI:
        posargs.append("--check")
    session.run("black", *posargs, *LINT_FILES)
    session.run("isort", *posargs, *LINT_FILES)


@nox.session
def typing(session: nox.Session):
    install(session, ".[typing]", editable=True)
    session.run("mypy", *LINT_FILES)
    session.run("basedpyright", f"src/{PROJECT}", "noxfile.py")


@nox.session
def bump(session: nox.Session):
    version = session.posargs[0]

    install(session, RELEASERR, "fclogr", "flit")
    session.run("releaserr", "--version")

    session.run("releaserr", "check-tag", version)
    session.run("releaserr", "ensure-clean")
    session.run("releaserr", "set-version", "-s", "file", version)

    install(session, ".", silent=False)

    # Bump specfile
    # fmt: off
    session.run(
        "fclogr", "bump",
        "--new", version,
        "--comment", f"Release {version}.",
        SPECFILE,
    )
    # fmt: on

    # Bump changelog, commit, and tag
    git(session, "add", SPECFILE, f"src/{PROJECT}/__init__.py")
    session.run("releaserr", "clog", version, "--tag")
    session.run("releaserr", "build", "--sign", "--backend", "flit_core")


@nox.session
def publish(session: nox.Session):
    # Setup
    install(session, RELEASERR, "twine")
    session.run("releaserr", "--version")

    session.run("releaserr", "ensure-clean")

    # Upload to PyPI
    session.run("releaserr", "upload")

    # Push to git, publish artifacts to sourcehut, and release to copr
    if not session.interactive or input(
        "Push to Sourcehut and copr build (Y/n)"
    ).lower() in ("", "y"):
        git(session, "push", "--follow-tags")
        session.run("hut", "git", "artifact", "upload", *iglob("dist/*"), external=True)
        copr_release(session)

    # Post-release bump
    session.run("releaserr", "post-version", "-s", "file")
    git(session, "add", f"src/{PROJECT}/__init__.py")
    git(session, "commit", "-S", "-m", "Post release version bump")


@nox.session
def copr_release(session: nox.Session):
    install(session, "copr-cli", "requests-gssapi", "specfile")
    tmp = Path(session.create_tmp())
    dest = tmp / SPECFILE
    copy2(SPECFILE, dest)
    session.run("python", "contrib/fedoraify.py", str(dest))
    session.run("copr-cli", "build", "--nowait", f"gotmax23/{PROJECT}", str(dest))


@nox.session
def srpm(session: nox.Session, posargs: Sequence[StrPath] | None = None):
    install(session, "fclogr")
    posargs = posargs or session.posargs
    session.run("fclogr", "--debug", "dev-srpm", *posargs, SPECFILE)


@nox.session
def mockbuild(session: nox.Session):
    tmp = Path(session.create_tmp())
    srpm(session, ("-o", tmp, "--keep"))
    margs = [
        "mock",
        "--spec",
        str(Path(tmp, SPECFILE)),
        "--source",
        str(tmp),
        *session.posargs,
    ]
    if not session.interactive:
        margs.append("--verbose")
    session.run(*margs, external=True)


@nox.session
def mkdocs(session: nox.Session) -> None:
    session.install("-r", "doc/requirements.in")
    session.run("mkdocs", *(session.posargs or ["build"]))


@nox.session
def releaserr(session: nox.Session):
    session.install("releaserr")
    session.run("releaserr", *session.posargs)
