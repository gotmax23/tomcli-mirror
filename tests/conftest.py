# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import pytest

from tomcli.toml import Reader, Writer


@pytest.fixture(name="reader", params=[member.value for member in Reader])
def parametrize_readers(request) -> str:
    return request.param


@pytest.fixture(name="writer", params=[member.value for member in Writer])
def parametrize_writers(request) -> str:
    return request.param


@pytest.fixture(name="rwargs")
def parametrize_rw(reader: str, writer: str) -> list[str]:
    return ["--reader", reader, "--writer", writer]
