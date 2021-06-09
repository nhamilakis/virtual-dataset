import json
import warnings
from pathlib import Path
from typing import Union, List, Dict, Optional

from ._core import mount, FileTargetList, FileTarget

try:
    import yaml
except ImportError:
    yaml = None


def load_dict_from_file(file_path: Union[str, Path]) -> Union[Dict, List]:
    if isinstance(file_path, str):
        file_path = Path(file_path)

    if file_path.suffix in ['.json']:
        with file_path.open() as fp:
            return json.load(fp)
    elif file_path.suffix in ['.yaml', '.yml']:
        if yaml is None:
            warnings.warn("The yaml module is not installed, cannot load a yaml file !!", RuntimeWarning, stacklevel=2)
            return {}
        else:
            with file_path.open() as fp:
                return yaml.load(fp, Loader=yaml.FullLoader)
    else:
        raise ValueError(f"{file_path.suffix} is not a known dict-like file type")


def key_extractor(obj: Dict, key: str):
    if key == "":
        return obj

    keys = key.split('.')
    for k in keys:
        if k in obj.keys():
            obj = obj[k]
        else:
            raise KeyError(f"{key} was not found in object !!")
    return obj


def mount_from_location(location: Union[str, Path], *,
                        file_regexp: Optional[List[str]] = None, keep_structure: bool = False,
                        tmp_prefix: Optional[Union[Path, str]] = None):
    if isinstance(location, str):
        location = Path(location)

    if not location.is_dir():
        raise ValueError(f'Location {location} does not exist')

    if file_regexp:
        files = []
        for rxp in file_regexp:
            files.extend(location.rglob(rxp))
    else:
        files = list(location.rglob("*"))

    # filter directories
    files = [f for f in files if f.is_file()]

    if keep_structure:
        file_list = FileTargetList([])
        for f in files:
            file_list.append(FileTarget(
                source_file=f,
                target_location=(f.relative_to(location)).parent
            ))
        files = file_list

    # return mount location
    return mount(files, tmp_prefix=tmp_prefix)


def mount_from_index_file(file_location: Union[str, Path], *,  key: Optional[str] = None,
                          tmp_prefix: Optional[Union[Path, str]] = None):
    if isinstance(file_location, str):
        file_location = Path(file_location)

    if not file_location.is_file():
        raise ValueError(f'File {file_location} does not exist')

    obj = load_dict_from_file(file_location)

    if key:
        obj = key_extractor(obj, key)

    # return mount location
    return mount(obj, tmp_prefix=tmp_prefix)

