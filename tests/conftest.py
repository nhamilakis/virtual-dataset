import shutil
from pathlib import Path
import tempfile

import pytest

# noinspection PyProtectedMember
import vdataset._mount_samples as cmd_file


@pytest.fixture(scope="function")
def test_files_20():
    location = Path(tempfile.mkdtemp())
    file_list = [
        location / f"file{x}.txt"
        for x in range(1, 20)
    ]
    for f in file_list:
        f.touch()
    # yield for testing
    yield file_list
    # clean up
    shutil.rmtree(location)


@pytest.fixture(scope="function")
def yaml_missing_cmd():
    # set yaml import to None
    tmp_yaml_mod = cmd_file.yaml
    cmd_file.yaml = None

    yield cmd_file

    # restore yaml mod
    cmd_file.yaml = tmp_yaml_mod


@pytest.fixture(scope="session")
def data_folder():
    data_dir = Path.cwd() / 'data'
    assert data_dir.is_dir(), "Data folder should be present to allow tests to be run"
    yield data_dir

