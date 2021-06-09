from vdataset import mount, unmount


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

    unmount(location, safe=True)
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
