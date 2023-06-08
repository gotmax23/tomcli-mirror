# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import os

import pytest

from tomcli.toml import AVAILABLE_READERS, AVAILABLE_WRITERS, Reader, Writer

ALLOW_SKIPS = os.environ.get("ALLOW_SKIPS", "1").lower() in ("true", "1")


@pytest.fixture(scope="session", autouse=True)
def check_deps():
    """
    Ensure that at least one reader and writer are available to avoid
    accidentially skipping every single test.
    """
    assert (
        AVAILABLE_READERS and AVAILABLE_WRITERS
    ), "There must be at least one reader and one writer available"


@pytest.fixture(name="reader", params=list(Reader))
def parametrize_readers(request) -> str:
    param = request.param
    if ALLOW_SKIPS and param not in AVAILABLE_READERS:
        pytest.skip(f"{param.value} is not available!")
    return request.param.value


@pytest.fixture(name="writer", params=list(Writer))
def parametrize_writers(request) -> str:
    param = request.param
    if ALLOW_SKIPS and param not in AVAILABLE_WRITERS:
        pytest.skip(f"{param.value} is not available!")
    return request.param.value


@pytest.fixture(name="rwargs")
def parametrize_rw(reader: str, writer: str) -> list[str]:
    return ["--reader", reader, "--writer", writer]
