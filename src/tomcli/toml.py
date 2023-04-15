# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import enum
import io
import sys
from collections.abc import Iterator, Mapping, MutableMapping
from contextlib import contextmanager
from types import ModuleType
from typing import IO, Any


class Reader(enum.Enum):
    """
    Libraries to use for deserializing TOML
    """

    TOMLLIB = "tomllib"
    TOMLKIT = "tomlkit"


class Writer(enum.Enum):
    """
    Libraries to use for serializing TOML
    """

    TOMLI_W = "tomli_w"
    TOMLKIT = "tomlkit"


DEFAULT_READER = Reader.TOMLKIT
DEFAULT_WRITER = Writer.TOMLKIT
NEEDS_STR: tuple[Writer | Reader, ...] = (Writer.TOMLKIT,)

AVAILABLE_READERS: dict[Reader, ModuleType] = {}
AVAILABLE_WRITERS: dict[Writer, ModuleType] = {}

if sys.version_info[:2] >= (3, 11):
    import tomllib

    AVAILABLE_READERS[Reader.TOMLLIB] = tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        pass
    else:
        AVAILABLE_READERS[Reader.TOMLLIB] = tomllib

try:
    import tomli_w
except ImportError:
    pass
else:
    AVAILABLE_WRITERS[Writer.TOMLI_W] = tomli_w

try:
    import tomlkit
except ImportError:
    pass
else:
    AVAILABLE_READERS[Reader.TOMLKIT] = tomlkit
    AVAILABLE_WRITERS[Writer.TOMLKIT] = tomlkit


@contextmanager
def _get_stream(fp: IO[bytes], backend: Reader | Writer) -> Iterator[IO[Any]]:
    if backend in NEEDS_STR:
        fp.flush()
        wrapper = io.TextIOWrapper(fp, "utf-8")
        try:
            yield wrapper
        finally:
            wrapper.flush()
            wrapper.detach()
    else:
        yield fp


def load(
    __fp: IO[bytes],
    prefered_reader: Reader | None = None,
    allow_fallback: bool = True,
) -> MutableMapping[str, Any]:
    """
    Parse a bytes stream containing TOML data

    Parameters:
        __fp:
            A bytes stream that supports `.read(). Positional argument only.
        prefered_reader:
            A [`Reader`][tomcli.toml.Reader] to use for parsing the TOML document
        allow_fallback:
            Whether to fallback to another Reader if `prefered_reader` is unavailable
    """
    prefered_reader = prefered_reader or DEFAULT_READER
    if not AVAILABLE_READERS:
        missing = ", ".join(module.value for module in Reader)
        raise ModuleNotFoundError(f"None of the following were found: {missing}")

    if prefered_reader in AVAILABLE_READERS:
        reader = prefered_reader
        mod = AVAILABLE_READERS[reader]
    elif not allow_fallback:
        raise ModuleNotFoundError(f"No module named {prefered_reader.value!r}")
    else:
        reader, mod = next(iter(AVAILABLE_READERS.items()))

    if hasattr(mod, "load"):
        with _get_stream(__fp, reader) as wrapper:
            return mod.load(wrapper)
    # Older versions of tomlkit
    else:
        txt = __fp.read().decode("utf-8")
        return mod.loads(txt)


def dump(
    __data: Mapping[str, Any],
    __fp: IO[bytes],
    prefered_writer: Writer | None = None,
    allow_fallback: bool = True,
) -> None:
    """
    Serialize an object to TOML and write it to a binary stream

    Parameters:
        __data:
            A Python object to serialize. Positional argument only.
        __fp:
            A bytes stream that supports `.write()`. Positional argument only.
        prefered_writer:
            A [`Writer`][tomcli.toml.Writer] to use for serializing the Python
            object
        allow_fallback:
            Whether to fallback to another Writer if `prefered_writer` is unavailable
    """
    prefered_writer = prefered_writer or DEFAULT_WRITER
    if not AVAILABLE_WRITERS:
        missing = ", ".join(module.value for module in Writer)
        raise ModuleNotFoundError(f"None of the following were found: {missing}")

    if prefered_writer in AVAILABLE_WRITERS:
        writer = prefered_writer
        mod = AVAILABLE_WRITERS[writer]
    elif not allow_fallback:
        raise ModuleNotFoundError(f"No module named {prefered_writer.value!r}")
    else:
        writer, mod = next(iter(AVAILABLE_WRITERS.items()))
    if hasattr(mod, "dump"):
        with _get_stream(__fp, writer) as wrapper:
            return mod.dump(__data, wrapper)
    # Older versions of tomlkit
    else:
        txt = mod.dumps(__data).encode("utf-8")
        __fp.write(txt)


def loads(
    __data: str,
    prefered_reader: Reader | None = None,
    allow_fallback: bool = True,
) -> MutableMapping[str, Any]:
    """
    Parse a string containing TOML data

    Parameters:
        __data:
            A string containing TOML data. Positional argument only.
        prefered_writer:
            A [`Writer`][tomcli.toml.Writer] to use for serializing the Python
            object
        allow_fallback:
            Whether to fallback to another Writer if `prefered_writer` is unavailable
    """
    prefered_reader = prefered_reader or DEFAULT_READER
    reader: Reader
    mod: ModuleType

    if not AVAILABLE_READERS:
        missing = ", ".join(module.value for module in Reader)
        raise ModuleNotFoundError(f"None of the following were found: {missing}")

    if prefered_reader in AVAILABLE_READERS:
        reader = prefered_reader
        mod = AVAILABLE_READERS[reader]
    elif not allow_fallback:
        raise ModuleNotFoundError(f"No module named {prefered_reader.value!r}")
    else:
        reader, mod = next(iter(AVAILABLE_READERS.items()))
    return mod.loads(__data)


def dumps(
    __data: Mapping[str, Any],
    prefered_writer: Writer | None = None,
    allow_fallback: bool = True,
) -> str:
    """
    Serialize an object to TOML and return it as a string

    Parameters:
        __data:
            A Python object to serialize. Positional argument only.
        prefered_writer:
            A [`Writer`][tomcli.toml.Writer] to use for serializing the Python
            object
        allow_fallback:
            Whether to fallback to another Writer if `prefered_writer` is unavailable
    """
    prefered_writer = prefered_writer or DEFAULT_WRITER
    if not AVAILABLE_WRITERS:
        missing = ", ".join(module.value for module in Writer)
        raise ModuleNotFoundError(f"None of the following were found: {missing}")

    if prefered_writer in AVAILABLE_WRITERS:
        writer = prefered_writer
        mod = AVAILABLE_WRITERS[writer]
    elif not allow_fallback:
        raise ModuleNotFoundError(f"No module named {prefered_writer.value!r}")
    else:
        writer, mod = next(iter(AVAILABLE_WRITERS.items()))
    return mod.dump(__data)
