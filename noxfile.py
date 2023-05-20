# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import argparse
import datetime
import os
from pathlib import Path
from shutil import copy2, rmtree
from textwrap import dedent

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


def install_fclogr(session: nox.Session):
    if Path("../fclogr").exists():
        install(session, "-e", "../fclogr")
    else:
        install(session, "git+https://git.sr.ht/~gotmax23/fclogr#main")


def git(session: nox.Session, *args, **kwargs):
    return session.run("git", *args, **kwargs, external=True)


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
    install(session, ".[all,tomli,test]", editable=True)
    session.run("pytest", "tests", *session.posargs)


@nox.session
def typing(session: nox.Session):
    install(session, ".[typing]", editable=True)
    session.run("mypy", "src")


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
    rmtree("dist", ignore_errors=True)

    session.run("hatch", "version", *session.posargs)
    version = session.run("hatch", "version", silent=True).strip()
    _check_git_tag(session, version)

    session.run(
        "rpmdev-bumpspec",
        "--new",
        version,
        "--comment",
        f"Release {version}.",
        f"{PROJECT}.spec",
        external=True,
    )

    session.run("hatch", "build", "--clean")
    _sign_artifacts(session)

    _, raw_frag_lines = add_frag(session, "FRAG.md", "NEWS.md", version)
    git_msg_file = _msg_tempfile(session, version, raw_frag_lines)

    session.run(
        "git",
        "add",
        "NEWS.md",
        f"src/{PROJECT}/__init__.py",
        f"{PROJECT}.spec",
        external=True,
    )
    session.run("git", "commit", "-S", "-m", f"Release {version}", external=True)
    ensure_clean(session)
    session.run(
        "git", "tag", "-s", "-F", git_msg_file, "--edit", f"v{version}", external=True
    )


def _sign_artifacts(session: nox.Session) -> None:
    uid = session.run("git", "config", "user.email", external=True, silent=True).strip()
    dist = Path("dist")
    artifacts = [str(p) for p in (*dist.glob("*.whl"), *dist.glob("*.tar.gz"))]
    for path in artifacts:
        if Path(path + ".asc").exists():
            session.warn(f"{path}.asc already exists. Not signing it.")
            continue
        session.run(
            "gpg", "--local-user", uid, "--armor", "--detach-sign", path, external=True
        )


@nox.session
def publish(session: nox.Session):
    # Setup
    ensure_clean(session)
    install(session, "hatch")
    session.run("hatch", "publish", *session.posargs)

    # Push to git
    if (
        not session.interactive
        or input("Push to Sourcehut and copr build (Y/n)").lower() != "n"
    ):
        git(session, "push", "--follow-tags")
        srht_artifacts.func(session)

        # Copr build
        copr_release.func(session)

    # Post-release bump
    session.run("hatch", "version", "post")
    git(session, "add", f"src/{PROJECT}/__init__.py")
    git(session, "commit", "-S", "-m", "Post release version bump")


@nox.session
def copr_release(session: nox.Session):
    install(session, "copr-cli", "requests-gssapi", "specfile")
    tmp = Path(session.create_tmp())
    dest = tmp / "tomcli.spec"
    copy2("tomcli.spec", dest)
    session.run("python", "contrib/fedoraify.py", dest)
    session.run("copr-cli", "build", "--nowait", "gotmax23/tomcli", str(dest))


@nox.session
def srht_artifacts(session: nox.Session):
    artifacts = map(str, Path("dist").glob("*"))
    session.run("hut", "git", "artifact", "upload", *artifacts, external=True)


@nox.session
def srpm(session: nox.Session, posargs=None):
    posargs = posargs or session.posargs
    install_fclogr(session)
    session.run("fclogr", "--debug", "dev-srpm", *posargs)


@nox.session
def mockbuild(session: nox.Session):
    tmp = Path(session.create_tmp())
    srpm.func(session, ("-o", tmp, "--keep"))
    spec_path = tmp / "tomcli.spec"
    margs = [
        "mock",
        "--spec",
        spec_path,
        "--source",
        tmp,
        *session.posargs,
    ]
    if not session.interactive:
        margs.append("--verbose")
    if not {
        "--clean",
        "--no-clean",
        "--cleanup-after",
        "--no-cleanup-after",
        "-n",
        "-N",
    } & set(session.posargs):
        margs.insert(1, "-N")
    session.run(*margs, external=True)


def rev_parse(session: nox.Session, key: str) -> str:
    return git(session, "rev-parse", key, silent=True).strip()


@nox.session
def copr_webhook(session: nox.Session):
    install(session, "requests")
    parser = argparse.ArgumentParser()
    parser.add_argument("url_file", type=Path)
    parser.add_argument("--skip-if-missing", action="store_true")
    parser.add_argument("-b", "--branch", action="append")
    args = parser.parse_args(session.posargs)
    if not args.url_file.is_file():
        msg = f"{args.url_file} does not exist"
        if args.skip_if_missing:
            session.warn(f"{msg}. Skipping...")
            return
        else:
            session.error(msg + "!")
    if args.branch:
        refs = [rev_parse(session, r) for r in args.branch]
        head = rev_parse(session, "HEAD")
        if head not in refs:
            session.warn(f"Skipping. This hook only runs on {args.branch}.")
            return
    code = """
    import sys
    from pathlib import Path

    import requests

    url = Path(sys.argv[1]).read_text().strip()
    requests.post(url, json={}).raise_for_status()
    """
    session.run("python", "-c", dedent(code), session.posargs[0])
