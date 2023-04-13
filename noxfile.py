# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import datetime
import os
from pathlib import Path

import nox

nox.options.sessions = ("formatters", "codeqa", "typing", "test")
nox.options.error_on_external_run = True


def check_env_var(name: str, default: bool = False):
    return os.environ.get(name, str(int(default))).lower() in ("1", "true")


PROJECT = "tomcli"
LINT_FILES = ("src", "tests", "noxfile.py")
IN_CI = "JOB_ID" in os.environ or check_env_var("IN_CI")
ALLOW_EDITABLE = check_env_var("ALLOW_EDITABLE", not IN_CI)


def install(session: nox.Session, *args, editable=False, **kwargs):
    if isinstance(session.virtualenv, nox.virtualenv.PassthroughEnv):
        session.warn(f"No venv. Skipping installation of {args}")
        return
    if editable and ALLOW_EDITABLE:
        args = ("-e", *args)
    session.install(*args, "-U", **kwargs)


@nox.session
def formatters(session: nox.Session):
    install(session, ".[formatters]")
    bargs = []
    rargs = ["--fix"]
    if IN_CI:
        bargs.append("--check")
        rargs.remove("--fix")
    session.run("black", *bargs, *LINT_FILES, "tests")
    session.run("ruff", "check", *rargs, "--select", "I", *LINT_FILES)


@nox.session
def codeqa(session: nox.Session):
    install(session, ".[codeqa]")
    session.run("ruff", *LINT_FILES, *session.posargs)
    session.run("reuse", "lint")


@nox.session(python=["3.7", "3.8", "3.9", "3.10", "3.11"])
def test(session: nox.Session):
    install(session, ".[all,test]", editable=True)
    session.run("pytest", "tests", *session.posargs)


@nox.session
def typing(session: nox.Session):
    install(session, ".[typing]", editable=True)


@nox.session
def lint(session: nox.Session):
    session.notify("formatters")
    session.notify("codeqa")
    session.notify("typing")


def add_frag(
    session: nox.Session, frag: str, file: str, version: str
) -> tuple[str, list[str]]:
    date = datetime.datetime.now(tz=datetime.timezone.utc).strftime("%Y-%m-%d")
    frag_heading = f"## {version} - {date} <a id={version!r}></a>\n"
    frag_lines: list[str] = [frag_heading, "\n"]
    with open(frag) as fp:
        raw_frag_lines = list(fp)
        frag_lines.extend(raw_frag_lines)
    lines: list[str] = []
    with open(file, "r+") as fp:
        needs_append = True
        for line in fp:
            if needs_append and line.startswith("##"):
                if frag_lines[0] != line:
                    lines.extend((*frag_lines, "\n"))
                needs_append = False
            lines.append(line)
        if needs_append:
            lines.extend(("\n", *frag_lines))
        fp.seek(0)
        fp.writelines(lines)
        fp.truncate()
    return frag_heading, raw_frag_lines


def format_git_msg(
    session: nox.Session, version: str, raw_frag_lines: list[str]
) -> list[str]:
    lines: list[str] = [f"{PROJECT} {version}\n", "\n", "\n"]
    for line in raw_frag_lines:
        if line.startswith("### "):
            line = line[4:].rstrip() + ":" + "\n"
        lines.append(line)
    return lines


def _msg_tempfile(session: nox.Session, version: str, raw_frag_lines: list[str]) -> str:
    text = "".join(format_git_msg(session, version, raw_frag_lines))
    tmp = session.create_tmp()
    path = Path(tmp, "GIT_TAG_MSG")
    path.write_text(text)
    return str(path)


def ensure_clean(session: nox.Session):
    if session.run(
        "git", "status", "--porcelain", "--untracked-files", silent=True, external=True
    ):
        msg = "There are untracked and/or modified files."
        session.error(msg)


def _check_git_tag(session: nox.Session, version: str):
    tag = "v" + version
    tags = session.run("git", "tag", "--list", external=True, silent=True).splitlines()
    if tag in tags:
        session.error(f"{tag} is already tagged")


@nox.session
def bump(session: nox.Session):
    ensure_clean(session)
    install(session, "hatch")
    session.run("hatch", "version", *session.posargs)
    version = session.run("hatch", "version", silent=True).strip()
    _check_git_tag(session, version)
    session.run("hatch", "build", "--clean")
    _, raw_frag_lines = add_frag(session, "FRAG.md", "NEWS.md", version)
    session.run("git", "add", "NEWS.md", f"src/{PROJECT}/__init__.py", external=True)
    session.run("git", "commit", "-S", "-m", f"Release {version}", external=True)
    git_msg_file = _msg_tempfile(session, version, raw_frag_lines)
    session.run(
        "git", "tag", "-s", "-F", git_msg_file, "--edit", f"v{version}", external=True
    )


def _sign_artifacts(session: nox.Session):
    uid = session.run("git", "config", "user.email", external=True, silent=True).strip()
    dist = Path("dist")
    artifacts = [str(p) for p in (*dist.glob("*.whl"), *dist.glob("*.tar.gz"))]
    for path in tuple(artifacts):
        session.run("gpg", "-u", uid, "--clearsign", path, external=True)
        artifacts.append(f"{path}.asc")


@nox.session
def publish(session: nox.Session):
    ensure_clean(session)
    install(session, "hatch")
    session.run("hatch", "build", "--clean")
    _sign_artifacts(session)
    session.run("hatch", "publish", *session.posargs)
    session.run("git", "push", "--follow-tags", external=True)
    session.run("hut", "git", "artifact", "upload", *artifacts, external=True)
    session.run("hatch", "version", "post")
    session.run("git", "add", f"src/{PROJECT}/__init__.py", external=True)
    session.run("git", "commit", "-S", "-m", "Post release version bump")
