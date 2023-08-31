# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import os
from pathlib import Path

import pytest

from tomcli.toml import AVAILABLE_READERS, AVAILABLE_WRITERS, Reader, Writer

ALLOW_SKIPS = os.environ.get("ALLOW_SKIPS", "1").lower() in ("true", "1")

HERE = Path(__file__).resolve().parent
TEST_DATA = HERE / "test_data"
ROOT = HERE.parent


@pytest.fixture(scope="session", autouse=True)
def check_deps():
    """
    Ensure that at least one reader and writer are available to avoid
    accidentially skipping every single test.
    """
    assert (
        AVAILABLE_READERS and AVAILABLE_WRITERS
    ), "There must be at least one reader and one writer available"


@pytest.fixture(name="reader_obj", params=list(Reader))
def parametrize_reader_objs(request) -> Reader:
    param = request.param
    if ALLOW_SKIPS and param not in AVAILABLE_READERS:
        pytest.skip(f"{param.value} is not available!")
    return request.param


@pytest.fixture(name="writer_obj", params=list(Writer))
def parametrize_writer_objs(request) -> Writer:
    param = request.param
    if ALLOW_SKIPS and param not in AVAILABLE_WRITERS:
        pytest.skip(f"{param.value} is not available!")
    return request.param


@pytest.fixture
def writer(writer_obj: Writer) -> str:
    return writer_obj.value


@pytest.fixture
def reader(reader_obj: Reader) -> str:
    return reader_obj.value


@pytest.fixture(name="rwargs")
def parametrize_rw(reader: str, writer: str) -> list[str]:
    return ["--reader", reader, "--writer", writer]


@pytest.fixture
def test_data() -> Path:
    return TEST_DATA
