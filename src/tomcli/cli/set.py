# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import dataclasses
import operator
import re
import sys
from collections.abc import Callable, Mapping, MutableMapping, MutableSequence, Sequence
from enum import Enum
from fnmatch import fnmatch
from types import SimpleNamespace
from typing import Any, TypeVar, cast

if sys.version_info >= (3, 10):
    from types import EllipsisType
else:
    EllipsisType = type(Ellipsis)

import click

from tomcli.cli._util import (
    DEFAULT_CONTEXT_SETTINGS,
    SHARED_PARAMS,
    RWEnumChoice,
    SharedArg,
    _std_cm,
    add_args_and_help,
    fatal,
    split_by_dot,
)
from tomcli.toml import Reader, Writer, dump, load


class PATTERN_TYPES(str, Enum):
    REGEX = "regex"
    FNMATCH = "fnmatch"


@dataclasses.dataclass()
class ModderCtx:
    path: str
    out: str
    reader: Reader | None = None
    writer: Writer | None = None
    allow_fallback_r: bool = True
    allow_fallback_w: bool = True

    def set_default_rw(self, reader: Reader, writer: Writer):
        if self.reader is None:
            self.reader = reader
        else:
            self.allow_fallback_r = False
        if self.writer is None:
            self.writer = writer
        else:
            self.allow_fallback_w = False

    def load(self) -> MutableMapping[str, Any]:
        with _std_cm(self.path, sys.stdin.buffer, "rb") as fp:
            return load(fp, self.reader, self.allow_fallback_r)

    def dump(self, __data: Mapping[str, Any]) -> None:
        with _std_cm(self.out, sys.stdout.buffer, "wb") as fp:
            dump(__data, fp, self.writer, self.allow_fallback_w)


@click.group(name="set", context_settings=DEFAULT_CONTEXT_SETTINGS)
@SHARED_PARAMS.version
@click.option(
    "-o",
    "--output",
    default=None,
    help="Where to output the data."
    " Defaults to outputting in place."
    " Use '-' to write to stdout.",
)
@SHARED_PARAMS.reader
@SHARED_PARAMS.writer
@click.pass_context
@add_args_and_help(SHARED_PARAMS.path)
def cli(
    context: click.Context,
    path: str,
    output: str,
    reader: Reader | None,
    writer: Writer | None,
):
    """
    Modify a TOML file
    """
    context.obj = ModderCtx(path, output or path, reader, writer)


@cli.group(name="lists")
def lsts():
    """
    Subcommands for creating and modifying lists
    """
    ...


@cli.command(name="del")
@click.pass_context
@add_args_and_help(SHARED_PARAMS.selector)
def delete(
    ctx: click.Context,
    selector: str,
):
    """
    Delete a value from a TOML file.
    """
    modder: ModderCtx = ctx.ensure_object(ModderCtx)
    modder.set_default_rw(Reader.TOMLKIT, Writer.TOMLKIT)
    fun_msg = "Thank you for your patronage, but we won't delete the whole file."
    set_type(
        callback=operator.delitem, fun_msg=fun_msg, modder=modder, selector=selector
    )


@cli.command(name="str")
@click.pass_context
@add_args_and_help(SHARED_PARAMS.selector, click.argument("value"))
def string(ctx: click.Context, selector: str, value: str):
    """
    Set a string value in a TOML file
    """
    modder: ModderCtx = ctx.ensure_object(ModderCtx)
    modder.set_default_rw(Reader.TOMLKIT, Writer.TOMLKIT)
    fun_msg = (
        "Your heart is in the right place,"
        " but we can't replace the whole file with a string"
    )
    return set_type(
        typ=str,
        default=dict,
        fun_msg=fun_msg,
        modder=modder,
        selector=selector,
        value=value,
    )


@cli.command(name="int")
@click.pass_context
@add_args_and_help(SHARED_PARAMS.selector, click.argument("value"))
def integer(ctx: click.Context, selector: str, value: str):
    """
    Set an integer value in a TOML file
    """
    fun_msg = (
        "Go outside and contemplate your choice"
        " to replace the whole file with integer."
    )
    modder: ModderCtx = ctx.ensure_object(ModderCtx)
    modder.set_default_rw(Reader.TOMLKIT, Writer.TOMLKIT)
    final: Any = value
    if "." in value:
        final = round(float(value))
    return set_type(
        typ=int,
        default=dict,
        fun_msg=fun_msg,
        modder=modder,
        selector=selector,
        value=final,
    )


@cli.command(name="float")
@click.pass_context
@add_args_and_help(SHARED_PARAMS.selector, click.argument("value"))
def float_(ctx: click.Context, selector: str, value: str):
    """
    Set a float value in a TOML file
    """
    fun_msg = (
        "I'll be very sad if you replace the whole TOML file with a float."
        " Computers have feelings too, ya know."
    )
    modder: ModderCtx = ctx.ensure_object(ModderCtx)
    modder.set_default_rw(Reader.TOMLKIT, Writer.TOMLKIT)
    return set_type(
        typ=float,
        default=dict,
        fun_msg=fun_msg,
        modder=modder,
        selector=selector,
        value=value,
    )


@cli.command(name="true")
@click.pass_context
@add_args_and_help(SHARED_PARAMS.selector)
def true(ctx: click.Context, selector: str):
    """
    Set a value to true in a TOML file
    """
    modder: ModderCtx = ctx.ensure_object(ModderCtx)
    modder.set_default_rw(Reader.TOMLKIT, Writer.TOMLKIT)
    return set_type(default=dict, modder=modder, selector=selector, value=True)


@cli.command(name="false")
@click.pass_context
@add_args_and_help(SHARED_PARAMS.selector)
def false(ctx: click.Context, selector: str):
    """
    Set a value to false in a TOML file
    """
    modder: ModderCtx = ctx.ensure_object(ModderCtx)
    modder.set_default_rw(Reader.TOMLKIT, Writer.TOMLKIT)
    return set_type(default=dict, modder=modder, selector=selector, value=False)


@cli.command(name="list")
@click.pass_context
@add_args_and_help(SHARED_PARAMS.selector, click.argument("value", nargs=-1))
def lst(ctx: click.Context, selector: str, value: tuple[str, ...]):
    """
    Create a list of strings in a TOML file
    """
    modder: ModderCtx = ctx.ensure_object(ModderCtx)
    modder.set_default_rw(Reader.TOMLKIT, Writer.TOMLKIT)
    fun_msg = (
        "A list is not a Mapping and therefore can't be the root."
        " Better luck next time!"
    )
    return set_type(
        # `value` should be a List[str], but typer passes a Tuple[str] :shrug:
        typ=list,
        default=dict,
        fun_msg=fun_msg,
        modder=modder,
        selector=selector,
        value=value,
    )


lsts.add_command(lst, name="str")


@cli.command()
@click.pass_context
@add_args_and_help(
    SHARED_PARAMS.selector, click.argument("value", nargs=-1, required=True)
)
def append(ctx: click.Context, selector: str, value: Sequence[str]):
    """
    Append strings to an existing list in a TOML file
    """
    modder: ModderCtx = ctx.ensure_object(ModderCtx)
    modder.set_default_rw(Reader.TOMLKIT, Writer.TOMLKIT)
    return set_type(
        fun_msg=None,
        modder=modder,
        selector=selector,
        value=value,
        callback=_append_callback,
    )


def _append_callback(cur: MutableMapping[str, Any], part: str, value: list[Any]):
    lst = cur.get(part)
    if not isinstance(lst, MutableSequence):
        fatal(
            "You can only append values to an existing list."
            " Use the 'list' subcommand to create a new list"
        )
    lst.extend(value)


_LISTS_COMMON_ARGS = SimpleNamespace(
    pattern=SharedArg(
        click.argument("pattern"),
        help="Pattern against which to match strings",
    ),
    pattern_type=click.option(
        "-t",
        "--type",
        "pattern_type",
        default=PATTERN_TYPES.REGEX,
        type=RWEnumChoice(PATTERN_TYPES),
    ),
    first=click.option(
        "--first / --no-first",
        default=False,
        help="Whether to only modify the first match or all matches",
    ),
)


@lsts.command(name="replace")
@click.pass_context
@_LISTS_COMMON_ARGS.pattern_type
@_LISTS_COMMON_ARGS.first
@add_args_and_help(
    SHARED_PARAMS.selector,
    _LISTS_COMMON_ARGS.pattern,
    SharedArg(click.argument("repl"), help="Replacement string"),
)
def lists_replace(
    ctx: click.Context,
    selector: str,
    pattern: str,
    repl: str,
    pattern_type: PATTERN_TYPES,
    first: bool,
):
    """
    Replace string values in a TOML list with other string values.
    Both Python regex and fnmatch style patterns are supported.
    """
    modder: ModderCtx = ctx.ensure_object(ModderCtx)
    modder.set_default_rw(Reader.TOMLKIT, Writer.TOMLKIT)
    cb = _repl_match_factory(pattern_type, first, pattern, repl)
    return set_type(
        fun_msg=None, modder=modder, selector=selector, value=..., callback=cb
    )


@lsts.command(name="delitem")
@click.pass_context
@_LISTS_COMMON_ARGS.pattern_type
@_LISTS_COMMON_ARGS.first
@add_args_and_help(SHARED_PARAMS.selector, _LISTS_COMMON_ARGS.pattern)
def lists_delete(
    ctx: click.Context,
    selector: str,
    pattern: str,
    pattern_type: PATTERN_TYPES,
    first: bool,
):
    """
    Delete string values in a TOML list.
    Both Python regex and fnmatch style patterns are supported.
    """
    modder: ModderCtx = ctx.ensure_object(ModderCtx)
    modder.set_default_rw(Reader.TOMLKIT, Writer.TOMLKIT)
    cb = _repl_match_factory(pattern_type, first, pattern, None)
    return set_type(
        fun_msg=None, modder=modder, selector=selector, value=..., callback=cb
    )


def _repl_match_factory(
    pattern_type: PATTERN_TYPES, first: bool, pattern: str, repl: str | None
) -> Callable[[MutableMapping[str, Any], str], None]:
    def callback(cur: MutableMapping[str, Any], part: str) -> None:
        if not isinstance(cur[part], MutableSequence):
            fatal("You cannot replace values unless the value is a list")
        lst: list[object] = cur[part]
        next_idx: int = 0
        for item in lst.copy():
            next_idx += 1
            if not isinstance(item, str):
                continue
            current_repl = repl
            match = False
            if pattern_type is PATTERN_TYPES.FNMATCH:
                match = fnmatch(item, pattern)
            elif pattern_type is PATTERN_TYPES.REGEX:  # noqa: SIM102
                if matcher := re.fullmatch(pattern, item):
                    match = True
                    if repl is not None:
                        current_repl = matcher.expand(repl)
            if match:
                if repl is None:
                    del lst[next_idx - 1]
                    next_idx -= 1
                else:
                    lst[next_idx - 1] = current_repl
                if first:
                    break

    return callback


T = TypeVar("T")


def set_type(  # noqa: PLR0913
    *,
    typ: Callable[[Any], T] = lambda x: x,
    callback: (
        Callable[[MutableMapping[str, Any], str, T], Any]
        | Callable[[MutableMapping[str, Any], str], Any]
    ) = operator.setitem,
    default: Callable[[], Any] | EllipsisType = ...,
    fun_msg: str | None = "Invalid selector: '.'",
    modder: ModderCtx,
    selector: str,
    value: Any = ...,
):
    """
    Iterate over a TOML file based on a dot-separated selector and preform on
    operation.

    Parameters:
        typ:
            Callable to use when passing `value` to the `callback` function
        callback:
            Callable to pass the final dictionary to.
            The callable should take three arguments:
                1. The final dictionary
                2. The final component of the dictionary
                3. The `value` passed to `set_type()`.
                   If `value` isn't passed, only two args will be passed.
        default:
            default factory to use when a key isn't found in the Mapping
            instead of raising a KeyError/ValueError
        fun_msg:
            Message to raise when the selector is `.`.
            Set this to `...` (Ellipsis) to proceed and pass
            the entire dictionary to the callback.
        modder:
            ModderCtx object
        selector:
            A dot separated map to a key in the TOML mapping.
            Example: `section1.subsection.value`
        value:
            value to pass as the third argument to the `callback`.

    """
    data = modder.load()
    cur = data
    parts = list(split_by_dot(selector))
    if selector == ".":
        if fun_msg:
            fatal(fun_msg)
        else:
            cur = {"data": cur}
            parts = ["data"]
    for idx, part in enumerate(parts):
        if idx + 1 == len(parts):
            break
        if part not in cur and default is not ...:
            cur[part] = cast("Callable[[], Any]", default)()
        cur = cur[part]
    if value is ...:
        callback(cur, part)  # type: ignore[call-arg]
    else:
        callback(cur, part, typ(value))  # type: ignore[call-arg]
    if selector == ".":
        data = data["data"]
    modder.dump(data)


app = cli
