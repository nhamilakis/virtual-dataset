#  Copyright (c) 2021.  Nicolas Hamilakis
""" Testing input parsing function """
from pathlib import Path


import pytest

# noinspection PyProtectedMember
from vdataset._mount_samples import key_extractor
# noinspection PyProtectedMember
from vdataset._core import parse_input, FileTarget


def test_parsing_invalid():
    obj = "/file/to/what"
    with pytest.raises(ValueError):
        _ = parse_input(obj, root_dir=Path('root'))


def test_parsing_no_parsing():
    obj = [
        FileTarget(source_file=Path('file1.txt'), target_location=Path('root/folder1/folder1_1')),
        FileTarget(source_file=Path('file2.txt'), target_location=Path('root/folder1/folder1_1')),
        FileTarget(source_file=Path('file3.txt'), target_location=Path('root/folder1/folder1_2')),
        FileTarget(source_file=Path('file4.txt'), target_location=Path('root/folder2'))
    ]
    parsed_list = parse_input(obj, root_dir=Path('root'))
    assert parsed_list[0].source_file == obj[0].source_file, "0. needs to be file1.txt"
    assert parsed_list[1].source_file == obj[1].source_file, "1. needs to be file2.txt"
    assert parsed_list[2].source_file == obj[2].source_file, "2. needs to be file3.txt"
    assert parsed_list[3].source_file == obj[3].source_file, "3. needs to be file4.txt"

    assert parsed_list[0].target_location == obj[0].target_location, "0. needs to be in root/folder1/folder1_1"
    assert parsed_list[1].target_location == obj[1].target_location, "1. needs to be in root/folder1/folder1_1"
    assert parsed_list[2].target_location == obj[2].target_location, "2. needs to be in root/folder1/folder1_2"
    assert parsed_list[3].target_location == obj[3].target_location, "3. needs to be in root/folder2"


def test_parsing_simple_list():
    obj = [
        "file1.txt",
        "file2.txt",
        "file3.txt"
    ]
    parsed_list = parse_input(obj, root_dir=Path('root'))
    # check files
    assert parsed_list[0].source_file == Path('file1.txt'), "First should be file1.txt"
    assert parsed_list[1].source_file == Path('file2.txt'), "First should be file1.txt"
    assert parsed_list[2].source_file == Path('file3.txt'), "First should be file1.txt"
    # check path to files
    assert parsed_list[0].target_location == Path('root'), "First should be in root/folder1/folder1_1"
    assert parsed_list[1].target_location == Path('root'), "First should be in root/folder1/folder1_1"
    assert parsed_list[2].target_location == Path('root'), "First should be in root/folder1/folder1_1"


def test_parsing_complex_tree():
    obj = {
        "folder1": {
            "folder1_1": ['file1.txt', 'file2.txt', {'folder1_1_1': 'file3.txt'}],
            "folder1_2": "file4.txt"
        },
        "folder2": "file5.txt"
    }
    parsed_list = parse_input(obj, root_dir=Path('root'))
    # check files
    assert parsed_list[0].source_file == Path('file1.txt'), "First should be file1.txt"
    assert parsed_list[1].source_file == Path('file2.txt'), "First should be file1.txt"
    assert parsed_list[2].source_file == Path('file3.txt'), "First should be file1.txt"
    assert parsed_list[3].source_file == Path('file4.txt'), "First should be file1.txt"
    assert parsed_list[4].source_file == Path('file5.txt'), "First should be file1.txt"
    # check path to files
    assert parsed_list[0].target_location == Path('root/folder1/folder1_1'), "First should be in root/folder1/folder1_1"
    assert parsed_list[1].target_location == Path('root/folder1/folder1_1'), "First should be in root/folder1/folder1_1"
    assert parsed_list[2].target_location == Path('root/folder1/folder1_1/folder1_1_1'), \
        "First should be in root/folder1/folder1_1"
    assert parsed_list[3].target_location == Path('root/folder1/folder1_2'), "First should be in root/folder1/folder1_1"
    assert parsed_list[4].target_location == Path('root/folder2'), "First should be in root/folder1/folder1_1"


def test_dict_extractor():
    obj = {
        "item1": {
            "item2": {
                "item3": "I am a value"
            }
        },
        "item4": {
            "item5": 65,
            "item6": 76
        },
        "item7": 129
    }
    assert obj["item1"]["item2"] == key_extractor(obj, "item1.item2"), "should be able to extract item1.item2 correctly"
    assert obj["item1"]["item2"]["item3"] == key_extractor(obj, "item1.item2.item3"), \
        "should be able to extract item1.item2.item3 correctly"
    assert key_extractor(obj, "item4.item5") == 65, "should be able to extract item4.item5 correctly"
    assert key_extractor(obj, "item4.item6") == 76, "should be able to extract item4.item6 correctly"
    assert key_extractor(obj, "item7") == 129, "should be able to extract item4.item6 correctly"

    assert key_extractor(obj, "") == obj, "Empty key should return the original dict"
    with pytest.raises(KeyError):
        key_extractor(obj, "item1.bad_item")

    with pytest.raises(KeyError):
        key_extractor(obj, "nonsense.is.never.a.good.key")
