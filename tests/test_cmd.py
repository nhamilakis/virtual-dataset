#  Copyright (c) 2021.  Nicolas Hamilakis

from pathlib import Path
import warnings

# noinspection PyProtectedMember
import pytest

import vdataset._mount_samples as cmd_file


def test_yaml_missing(yaml_missing_cmd):

    with warnings.catch_warnings(record=True) as w:
        # Cause all warnings to always be triggered.
        warnings.simplefilter("always")
        result = yaml_missing_cmd.load_dict_from_file(Path('some_file.yaml'))

        assert len(w) == 1, "Warning object should exist"
        assert issubclass(w[-1].category, RuntimeWarning), "Warning should be of type RuntimeWarning"
        assert "yaml" in str(w[-1].message), "Warning message should be about yaml loading"
        assert result == {}, "result should be an empty dictionary"


def test_dict_loading(data_folder):
    obj = cmd_file.load_dict_from_file(data_folder / 'test1.json')
    assert isinstance(obj, (dict, list)), "Object test1.json should load correctly"

    if cmd_file.yaml is not None:
        obj = cmd_file.load_dict_from_file(str(data_folder / 'test1.yaml'))
        assert isinstance(obj, (dict, list)), "Object test1.yaml should load correctly"

    with pytest.raises(ValueError):
        _ = cmd_file.load_dict_from_file(data_folder / 'repo1/file1.txt')


def test_yaml_loading():
    if cmd_file.yaml is not None:
        file = Path('data/test1.yaml')
        if not file.is_file():
            warnings.warn('File loading could not be tested as data folder is missing')
            return

        item = cmd_file.load_dict_from_file(file)
        assert isinstance(item, dict), "result should be a dict"
        assert 'files' in item.keys(), "files should be a key in the dict"
        assert isinstance(item["files"], list), "dict['files'] should be a list"
        assert len(item["files"]) == 5, "list should be of size 5"


def test_json_loading(data_folder):
    file = data_folder / 'test1.json'
    if not file.is_file():
        warnings.warn('File loading could not be tested as data folder is missing')
        return

    item = cmd_file.load_dict_from_file(file)
    assert isinstance(item, dict), "result should be a dict"
    assert 'files' in item.keys(), "files should be a key in the dict"
    assert isinstance(item["files"], list), "dict['files'] should be a list"
    assert len(item["files"]) == 5, "list should be of size 5"
