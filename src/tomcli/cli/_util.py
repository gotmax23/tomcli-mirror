# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import sys
from collections.abc import Iterator
from contextlib import contextmanager
from typing import IO, AnyStr, NoReturn, cast

from typer import Exit


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
