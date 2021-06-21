#  Copyright (c) 2021.  Nicolas Hamilakis

from pathlib import Path

import pytest

from vdataset import (
    mount, unmount, mount_from_index_file,
    mount_from_location
)


def test_file_fixture(test_files_20):
    for f in test_files_20:
        assert f.is_file(), f"{f} should be a file"


def test_mount(test_files_20):
    location = mount(test_files_20)

    for f in location.glob("*.txt"):
        assert f.is_symlink(), f"{f} should be a symlink"
        assert f.resolve() in test_files_20, f"{f.resolve()} should be in source list"

    unmount(location, safe=True)
    assert not location.is_dir(), f"{location} should have been deleted"


def test_mount_with_prefix(test_files_20):
    with pytest.raises(ValueError):
        _ = mount(test_files_20, tmp_prefix="/somewhere/in/the/void")

    temp_location = Path.cwd() / 'tmp_test'
    temp_location.mkdir(exist_ok=True, parents=True)

    location = mount(test_files_20, tmp_prefix=str(temp_location))

    for f in location.glob("*.txt"):
        assert f.is_symlink(), f"{f} should be a symlink"
        assert f.resolve() in test_files_20, f"{f.resolve()} should be in source list"

    unmount(location, safe=True)
    assert not location.is_dir(), f"{location} should have been deleted"

    temp_location.rmdir()
    assert not temp_location.is_dir(), f"{temp_location} should not exist after clean-up"


def test_complex_mount(test_files_20):
    obj = {
        "dir1": test_files_20[:4],
        "dir2": test_files_20[4:9],
        "dir3": {
            "subDir1": test_files_20[9:15],
            "subDir2": test_files_20[-1],
        },
        "dir4": test_files_20[15:-1]
    }
    location = mount(obj)

    assert (location / 'dir1').is_dir(), f"{location / 'dir1'} should exist !"
    for f in (location / 'dir1').glob("*.txt"):
        assert f.is_symlink(), f"{f} should be a symlink"
        assert f.resolve() in test_files_20[:4], f"{f.resolve()} should be in source list"

    assert (location / 'dir2').is_dir(), f"{location / 'dir2'} should exist !"
    for f in (location / 'dir2').glob("*.txt"):
        assert f.is_symlink(), f"{f} should be a symlink"
        assert f.resolve() in test_files_20[4:9], f"{f.resolve()} should be in source list"

    assert (location / 'dir3').is_dir(), f"{location / 'dir3'} should exist !"
    assert (location / 'dir3' / 'subDir1').is_dir(), f"{location / 'dir3' / 'subDir1'} should exist !"
    for f in (location / 'dir3' / 'subDir1').glob("*.txt"):
        assert f.is_symlink(), f"{f} should be a symlink"
        assert f.resolve() in test_files_20[9:15], f"{f.resolve()} should be in source list"

    assert (location / 'dir3' / 'subDir2').is_dir(), f"{location / 'dir3' / 'subDir2'} should exist !"

    sub2_file = (location / 'dir3' / 'subDir2' / test_files_20[-1].name)
    assert sub2_file.is_symlink(), f"{sub2_file} must be a symlink"
    assert sub2_file.resolve() == test_files_20[-1]

    unmount(location, safe=True)
    assert not location.is_dir(), f"{location} should have been deleted"


def test_safety_unmount(test_files_20):
    location = mount(test_files_20)

    (location / 'annoying_file.txt').touch()

    # make location str to test if conversion works
    unmount(str(location), safe=True)
    assert location.is_dir(), f"{location} should not have been deleted in safe mode"

    (location / 'annoying_file.txt').unlink()

    unmount(location, safe=True)
    assert not location.is_dir(), f"{location} should have been deleted"


def test_unsafe_unmount(test_files_20):
    location = mount(test_files_20)
    # unmount unsafe should delete always
    unmount(location, safe=False)
    assert not location.is_dir(), f"{location} should have been deleted in unsafe mode"

    location = mount(test_files_20)
    # add non symlink file in the location folder
    (location / 'annoying_file.txt').touch()

    unmount(location, safe=False)
    assert not location.is_dir(), f"{location} should have been deleted in unsafe mode"


def test_mount_invalid_location():
    with pytest.raises(ValueError):
        _ = mount_from_location(Path("/fake/folder"))


def test_mount_from_location_simple(data_folder):
    location = mount_from_location(str(data_folder))

    assert location.is_dir(), "mounting point must exist"
    file_list = [f for f in data_folder.rglob('*') if f.is_file()]

    for item in location.rglob("*"):
        if item.is_file():
            assert item.resolve() in file_list, f"symlink {item} should point to original file in {data_folder}"

    unmount(location)
    assert not location.is_dir(), f"{location} should have been unmounted"


def test_mount_from_location_keep_structure(data_folder):
    location = mount_from_location(data_folder, keep_structure=True)
    assert location.is_dir(), "mounting point must exist"
    assert (location / 'repo1' / 'repo1.1').is_dir(), "directory repo1/repo1.1 should exist in mount location"
    assert (location / 'repo2').is_dir(), "directory repo2 should exist in mount location"

    file_list = [f for f in data_folder.rglob('*') if f.is_file()]

    for item in location.rglob("*"):
        if item.is_file():
            assert item.resolve() in file_list, f"symlink {item} should point to original file in {data_folder}"

    unmount(location)
    assert not location.is_dir(), f"{location} should have been unmounted"


def test_mount_from_location_only_txt_files(data_folder):
    location = mount_from_location(data_folder, file_regexp=["*.txt"])
    assert location.is_dir(), "mounting point must exist"

    file_list = [f for f in data_folder.rglob('*.txt') if f.is_file()]

    for item in location.rglob("*"):
        if item.is_file():
            assert item.resolve() in file_list, f"symlink {item} should point to original file in {data_folder}"

    unmount(location)
    assert not location.is_dir(), f"{location} should have been unmounted"


def test_mount_index_bad_file(data_folder):
    with pytest.raises(ValueError):
        _ = mount_from_index_file("file.yaml")

    with pytest.raises(ValueError):
        _ = mount_from_index_file(data_folder / 'bad_test.toml')


def test_mount_json_simple(data_folder):
    location = mount_from_index_file(data_folder / 'simple.json')
    assert location.is_dir(), "mounting point must exist"

    unmount(location)
    assert not location.is_dir(), f"{location} should have been unmounted"


def test_mount_yml_simple(data_folder):
    location = mount_from_index_file(data_folder / 'simple.yaml')
    assert location.is_dir(), "mounting point must exist"

    unmount(location)
    assert not location.is_dir(), f"{location} should have been unmounted"


def test_mount_json_complex(data_folder):
    location = mount_from_index_file(data_folder / 'complex.json')
    assert location.is_dir(), "mounting point must exist"

    unmount(location)
    assert not location.is_dir(), f"{location} should have been unmounted"
