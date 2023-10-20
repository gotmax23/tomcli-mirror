# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: MIT

from __future__ import annotations

import sys
from typing import Any

import pytest

from tomcli.formatters import FormatterError, get_formatters_list
from tomcli.formatters.builtin import newline_list_formatter

if sys.version_info >= (3, 11):
    import importlib.metadata as importlib_metadata
else:
    import importlib_metadata

eps = get_formatters_list()
eps_params = [pytest.param(ep, id=ep.name) for ep in eps]


@pytest.mark.parametrize("formatter", eps_params)
def test_get_all_formatters(formatter: importlib_metadata.EntryPoint) -> None:
    formatter.load()


def test_newline_list_formatter():
    obj = ["abc", 123, 123.0]
    expected = "abc\n123\n123.0"
    assert newline_list_formatter(obj) == expected


@pytest.mark.parametrize(
    "obj,err",
    [
        pytest.param(
            {"not": "a list"},
            "The object is not a list",
        ),
        pytest.param(
            ["Random", object()],
            "<class 'object'> cannot be represented by a newline-separated list",
        ),
    ],
)
def test_newline_list_formatter_error(obj: Any, err: str) -> None:
    with pytest.raises(FormatterError, match=err):
        newline_list_formatter(obj)
