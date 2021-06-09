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
# todo check typing to maybe separate final product from inputs to allow all types to be inserted into parser


def parse_input(file_object: FileList, root_dir: Path) -> FileTargetList:
    """ Builds a FileTarget list from a dict or list object """
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
    if isinstance(tmp_prefix, str):
        tmp_prefix = Path(tmp_prefix)

    if tmp_prefix and not tmp_prefix.is_dir():
        raise ValueError(f'Prefix must be a valid directory')

    # make root dir
    root_dir = Path(tempfile.mkdtemp(prefix=tmp_prefix))

    file_list: FileTargetList = parse_input(input_files, root_dir)

    for item in file_list:
        # create folder if necessary
        item.target_location.mkdir(exist_ok=True, parents=True)
        # symlink
        (item.target_location / item.source_file.name).symlink_to(item.source_file)

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
