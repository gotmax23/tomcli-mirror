# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import IO, AnyStr, cast


@contextmanager
def _std_cm(path: str, dash_stream: IO[AnyStr], mode: str) -> Iterator[IO[AnyStr]]:
    if str(path) == "-":
        yield dash_stream
    else:
        with open(path, mode) as fp:
            yield cast(IO[AnyStr], fp)
