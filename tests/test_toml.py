# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: MIT

from __future__ import annotations

from pathlib import Path

import pytest

from tomcli.toml import Reader, Writer, _get_reader, _get_writer, dumps, loads


def test_toml_loads_and_dumps(
    writer_obj: Writer, reader_obj: Reader, test_data: Path, tmp_path: Path
):
    path = test_data / "test1.toml"
    data = loads(path.read_text(), prefered_reader=reader_obj, allow_fallback=False)
    dumped = dumps(data, prefered_writer=writer_obj, allow_fallback=False)
    data2 = loads(dumped, prefered_reader=reader_obj, allow_fallback=False)
    assert data == data2


def test_get_reader_missing(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("tomcli.toml.AVAILABLE_READERS", {})
    with pytest.raises(
        ModuleNotFoundError, match="None of the following were found: tomllib, tomlkit"
    ):
        _get_reader(None, True)


def test_get_writer_missing_preferred(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("tomcli.toml.AVAILABLE_WRITERS", {Writer.TOMLKIT: object()})
    with pytest.raises(ModuleNotFoundError, match="No module named 'tomli_w'"):
        _get_writer(Writer.TOMLI_W, False)


def test_get_writer_missing_fallback(monkeypatch: pytest.MonkeyPatch):
    mod = object()
    monkeypatch.setattr("tomcli.toml.AVAILABLE_WRITERS", {Writer.TOMLKIT: mod})
    assert _get_writer(Writer.TOMLI_W, True) == (Writer.TOMLKIT, mod)
