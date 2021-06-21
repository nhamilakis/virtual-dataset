#  Copyright (c) 2021.  Nicolas Hamilakis

import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import NewType, List, Union, Dict, Optional


# typing
@dataclass
class FileTarget:
    source_file: Union[Path, str]
    target_location: Union[Path, str]


FileTargetList = NewType('FileTargetList', List[FileTarget])
FileList = NewType('FileList', Union[FileTargetList, List[Union[Path, str]]])


def parse_input(file_object: FileList, root_dir: Path) -> FileTargetList:
    """  Builds a FileTarget list from a dict or list object
    :param file_object: the object to parse
    :param root_dir: the root directory to use a the target location
    :return: FileTargetList
    """
    result = FileTargetList([])
    if isinstance(file_object, dict):
        for key, value in file_object.items():
            if isinstance(value, (dict, list)):
                result.extend(parse_input(value, (root_dir / key)))
            elif isinstance(value, (str, Path)):
                result.append(FileTarget(source_file=Path(value), target_location=(root_dir / key)))
    elif isinstance(file_object, list):
        for item in file_object:
            if isinstance(item, (dict, list)):
                result.extend(parse_input(item, root_dir))
            elif isinstance(item, (str, Path)):
                result.append(FileTarget(source_file=Path(item), target_location=root_dir))
            elif isinstance(item, FileTarget):
                result.append(item)
    else:
        raise ValueError('Unknown value given')
    return result


def mount(input_files: Union[FileList, Dict], *, tmp_prefix: Optional[Union[Path, str]] = None) -> Optional[Path]:
    """ Creates a virtual dataset from input file list

    :param input_files: list of files to include in the mounted dataset
    :param tmp_prefix: prefix of location to create the temporary files
    :return: location of the new virtual dataset
    """
    if isinstance(tmp_prefix, str):
        tmp_prefix = Path(tmp_prefix)

    if tmp_prefix and not tmp_prefix.is_dir():
        raise ValueError(f'Prefix {tmp_prefix} must be a valid directory')

    # make root dir
    if tmp_prefix:
        root_dir = Path(tempfile.mkdtemp(prefix=f"{tmp_prefix}/"))
    else:
        root_dir = Path(tempfile.mkdtemp())

    file_list: FileTargetList = parse_input(input_files, root_dir)

    for item in file_list:
        # create folder if necessary
        location = root_dir / item.target_location
        location.mkdir(exist_ok=True, parents=True)
        # symlink
        (location / item.source_file.name).symlink_to(item.source_file.resolve())

    # return root location
    return root_dir


def unmount(location: Union[str, Path], *, safe: bool = True):
    """ Unmount a dataset folder.

    :param location: location of dataset to unmount
    :param safe: Safe mode prevents deletion if non symlink files are found in the dataset (default True).
    """
    if isinstance(location, str):
        location = Path(location)

    try:
        if safe:
            for file in location.rglob("*"):
                if not file.is_dir() and not file.is_symlink():
                    raise ValueError('found non symlink files')

        shutil.rmtree(location)
    except ValueError:
        print(f"Found non symlink files in {location}, safe mode skipped deletion")
