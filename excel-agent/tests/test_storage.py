import pytest
import json
from pathlib import Path
from src.storage.file_storage import read_json, write_json, append_json_list


def test_write_and_read(tmp_path):
    path = tmp_path / "test.json"
    data = {"key": "value", "num": 42}
    write_json(path, data)
    result = read_json(path)
    assert result == data


def test_read_nonexistent(tmp_path):
    path = tmp_path / "nonexistent.json"
    result = read_json(path)
    assert result is None


def test_append_json_list(tmp_path):
    path = tmp_path / "list.json"
    append_json_list(path, [{"a": 1}])
    append_json_list(path, [{"b": 2}])
    result = read_json(path)
    assert len(result) == 2
    assert result[0] == {"a": 1}
    assert result[1] == {"b": 2}


def test_atomic_write(tmp_path):
    path = tmp_path / "atomic.json"
    write_json(path, {"v": 1})
    write_json(path, {"v": 2})
    assert read_json(path) == {"v": 2}
