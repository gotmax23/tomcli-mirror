# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import sys
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum
from textwrap import dedent
from types import SimpleNamespace
from typing import IO, TYPE_CHECKING, Any, AnyStr, NoReturn, TypeVar, cast

import click

from tomcli import __version__ as _ver
from tomcli._peekable import peekable
from tomcli.formatters import DEFAULT_FORMATTER
from tomcli.toml import Reader, Writer

_T = TypeVar("_T")
if TYPE_CHECKING:
    from typing_extensions import ParamSpec

    _P = ParamSpec("_P")


DEFAULT_CONTEXT_SETTINGS = context_settings = dict(help_option_names=["-h", "--help"])


@contextmanager
def _std_cm(path: str, dash_stream: IO[AnyStr], mode: str) -> Iterator[IO[AnyStr]]:
    if str(path) == "-":
        yield dash_stream
    else:
        with open(path, mode) as fp:
            yield cast(IO[AnyStr], fp)


def fatal(*args: object, returncode: int = 1) -> NoReturn:
    print(*args, file=sys.stderr)
    click.get_current_context().exit(returncode)


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


# Based on https://github.com/pallets/click/pull/2210 and
# https://github.com/pallets/click/issues/605
# Copyright 2014 Pallets and Click contributors
class RWEnumChoice(click.Choice):
    def __init__(
        self,
        enum_type: type[Enum],
        case_sensitive: bool = True,
        force_lowercase: bool = True,
    ):
        super().__init__(
            choices=[
                element.name.lower() if force_lowercase else element.name
                for element in enum_type
            ],
            case_sensitive=case_sensitive,
        )
        self.enum_type = enum_type
        self.force_lowercase: bool = force_lowercase

    def convert(
        self, value: Any, param: click.Parameter | None, ctx: click.Context | None
    ) -> Any:
        value = super().convert(value=value, param=param, ctx=ctx)
        if value is None:
            return None
        return self.enum_type[value.upper() if self.force_lowercase else value]


@dataclass
class SharedArg:
    param: Any
    help: str | None = None  # noqa: A003

    def __call__(self, func: Callable[_P, _T]) -> Callable[_P, _T]:
        return self.param(func)


def add_args_and_help(
    *params: SharedArg | Any,
) -> Callable[[Callable[_P, _T]], Callable[_P, _T]]:
    def inner(func: Callable[_P, _T]) -> Callable[_P, _T]:
        helps: list[str] = []
        for param in reversed(params):
            param(func)
            metavar = func.__click_params__[-1].make_metavar()  # type: ignore[attr-defined]
            phelp = f"* {metavar}"
            if isinstance(param, SharedArg) and param.help:
                phelp += f": {param.help}"
            helps.append(phelp)
        helps.reverse()
        func.__doc__ = dedent(func.__doc__) + "\n\n" if func.__doc__ else ""
        func.__doc__ += "\n\n".join(helps)
        return func

    return inner


SELECTOR_HELP = (
    "A dot separated map to a key in the TOML mapping."
    " Example: 'section1.subsection.value'"
)


SHARED_PARAMS = SimpleNamespace(
    writer=click.option("--writer", default=None, type=RWEnumChoice(Writer)),
    reader=click.option("--reader", default=None, type=RWEnumChoice(Reader)),
    path=SharedArg(
        click.argument("path"),
        help="Path to a TOML file to read. Use '-' to read from stdin."
        " Set to `...` when calling `--help` for a subcommand",
    ),
    selector=SharedArg(
        click.argument("selector"),
        help=SELECTOR_HELP,
    ),
    formatter=click.option("-F", "--formatter", default=DEFAULT_FORMATTER),
    version=click.version_option(_ver, message="%(version)s"),
)


__all__ = (
    "DEFAULT_CONTEXT_SETTINGS",
    "_std_cm",
    "fatal",
    "RWEnumChoice",
    "SharedArg",
    "add_args_and_help",
    "SELECTOR_HELP",
    "SHARED_PARAMS",
)
