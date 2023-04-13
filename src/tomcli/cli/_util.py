# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

from collections.abc import Iterable
from contextlib import contextmanager
from typing import IO, Any


@contextmanager
def _std_cm(path: str, dash_stream: str, mode: str) -> Iterable[IO[Any]]:
    if str(path) == "-":
        yield dash_stream
    else:
        with open(path, mode) as fp:
            yield fp
