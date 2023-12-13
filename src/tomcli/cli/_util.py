# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import sys
from collections.abc import Iterator
from contextlib import contextmanager
from typing import IO, AnyStr, NoReturn, cast

from more_itertools import peekable
from typer import Exit

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated


@contextmanager
def _std_cm(path: str, dash_stream: IO[AnyStr], mode: str) -> Iterator[IO[AnyStr]]:
    if str(path) == "-":
        yield dash_stream
    else:
        with open(path, mode) as fp:
            yield cast(IO[AnyStr], fp)


def fatal(*args: object, returncode: int = 1) -> NoReturn:
    print(*args, file=sys.stderr)
    raise Exit(returncode)


def version_cb(val: bool):
    if not val:
        return

    from tomcli import __version__ as ver

    print(ver)
    raise Exit


def split_by_dot(selector: str) -> Iterator[str]:
    """
    Naively split dot-separated keys while keeping quotes in mind.

    >>> list(split_by_dot("a.b"))
    ['a', 'b']
    >>> list(split_by_dot("'a.b'"))
    ['a.b']
    >>> list(split_by_dot('"a.b".c'))
    ['a.b', 'c']
    >>> list(split_by_dot("'ab'x"))
    Traceback (most recent call last):
        ...
    ValueError: Invalid selector part: `'ab'x`. Expected `.` or end but got `x`.
    >>> list(split_by_dot("a.b.."))
    Traceback (most recent call last):
        ...
    ValueError: Invalid selector part: `b..`. Expected character or end but got `.`.
    """

    quotes = ("'", '"')
    quote: str | None = None
    it = peekable(selector)
    parts = ""

    def _err(part: str, expected: str, but: str | None = None) -> NoReturn:
        but = but if but is not None else it.peek()
        msg = f"Invalid selector part: `{part}`. Expected {expected} but got `{but}`."
        raise ValueError(msg)

    for character in it:
        if character == quote:
            # Don't allow something like `"ab"c.d`.
            if it.peek(...) not in (".", ...):
                _err(quote + parts + quote + it.peek(), "`.` or end")
            quote = None
            # Short circuit. We know the next is a "."
            yield parts
            parts = ""
            next(it, ...)
        elif quote is None and character == ".":
            if it.peek(...) == ".":
                _err(parts + "..", "character or end")
            yield parts
            parts = ""
        elif character in quotes:
            quote = character
        else:
            parts += character
    if parts:
        yield parts


__all__ = ("_std_cm", "fatal", "version_cb", "Annotated")
