# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import dataclasses
import operator
import re
import sys
from collections.abc import Callable, Mapping, MutableMapping, MutableSequence
from enum import Enum
from fnmatch import fnmatch
from typing import Any, List, Optional, TypeVar

if sys.version_info >= (3, 10):
    from types import EllipsisType
else:
    EllipsisType = type(Ellipsis)

from typer import Argument, Context, Option, Typer

from tomcli.cli._util import _std_cm, fatal
from tomcli.toml import Reader, Writer, dump, load

app = Typer(context_settings=dict(help_option_names=["-h", "--help"]))
lists = Typer(help="Subcommands to manage lists in TOML files")
app.add_typer(lists, name="lists")

SELECTOR_HELP = (
    "A dot separated map to a key in the TOML mapping."
    " Example: 'section1.subsection.value'"
)


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


@app.callback()
def callback(
    ctx: Context,
    path: str = Argument(
        ..., help="Path to a TOML file to read. Use '-' to read from stdin."
    ),
    output: Optional[str] = Option(
        None,
        "-o",
        "--output",
        help="Where to output the data."
        " Defaults to outputting in place."
        " Use '-' to write to stdout.",
    ),
    reader: Optional[Reader] = None,
    writer: Optional[Writer] = None,
):
    ctx.obj = ModderCtx(path, output or path, reader, writer)


@app.command(name="del")
def delete(
    ctx: Context,
    selector: str = Argument(..., help=SELECTOR_HELP),
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


@app.command(name="str")
def string(
    ctx: Context,
    selector: str = Argument(..., help=SELECTOR_HELP),
    value: str = Argument(...),
):
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


@app.command(name="int")
def integer(
    ctx: Context,
    selector: str = Argument(..., help=SELECTOR_HELP),
    value: str = Argument(...),
):
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


@app.command(name="float")
def float_(
    ctx: Context,
    selector: str = Argument(..., help=SELECTOR_HELP),
    value: float = Argument(...),
):
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


@app.command(name="list")
@lists.command(name="str")
def lst(
    ctx: Context,
    selector: str = Argument(..., help=SELECTOR_HELP),
    value: List[str] = Argument(...),
):
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


@app.command()
def append(
    ctx: Context,
    selector: str = Argument(..., help=SELECTOR_HELP),
    value: List[str] = Argument(...),
):
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


@lists.command(name="replace")
def lists_replace(
    ctx: Context,
    selector: str = Argument(..., help=SELECTOR_HELP),
    pattern: str = Argument(..., help="Pattern against which to match strings"),
    repl: str = Argument(..., help="Replacement string"),
    pattern_type: PATTERN_TYPES = Option(PATTERN_TYPES.REGEX, "-t", "--type"),
    first: bool = Option(
        False, help="Whether to only modify the first match or all matches"
    ),
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


def _repl_match_factory(
    pattern_type: PATTERN_TYPES, first: bool, pattern: str, repl: str
) -> Callable[[MutableMapping[str, Any], str], None]:
    def callback(cur: MutableMapping[str, Any], part: str) -> None:
        if not isinstance(cur[part], MutableSequence):
            fatal("You cannot replace values unless the value is a list")
        lst: MutableSequence[object] = cur[part]
        for idx, item in enumerate(lst):
            if not isinstance(item, str):
                continue
            current_repl = repl
            match = False
            if pattern_type is PATTERN_TYPES.FNMATCH:
                match = fnmatch(item, pattern)
            elif pattern_type is PATTERN_TYPES.REGEX:  # noqa: SIM102
                if matcher := re.fullmatch(pattern, item):
                    match = True
                    current_repl = matcher.expand(repl)
            if match:
                lst[idx] = current_repl
                if first:
                    break

    return callback


T = TypeVar("T")


def set_type(  # noqa: PLR0913
    *,
    typ: Callable[[Any], T] = lambda x: x,
    callback: Callable[[MutableMapping[str, Any], str, T], Any]
    | Callable[[MutableMapping[str, Any], str], Any] = operator.setitem,
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
    parts = selector.split(".")
    if selector == ".":
        if fun_msg:
            fatal(fun_msg)
        else:
            cur = {"data": cur}
            parts = ["data"]
    idx = 0
    for idx, part in enumerate(parts):
        if idx + 1 == len(parts):
            break
        if part not in cur and default is not ...:
            cur[part] = default()
        cur = cur[part]
    if value is ...:
        callback(cur, part)  # type: ignore[call-arg]
    else:
        callback(cur, part, typ(value))  # type: ignore[call-arg]
    if selector == ".":
        data = data["data"]
    modder.dump(data)
