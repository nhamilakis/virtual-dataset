# Virtual Dataset


[![PyPI version](https://badge.fury.io/py/virtual-dataset.svg)](https://badge.fury.io/py/virtual-dataset) [![Test & Build](https://github.com/nhamilakis/virtual-dataset/actions/workflows/test_and_build.yml/badge.svg)](https://github.com/nhamilakis/virtual-dataset/actions/workflows/test_and_build.yml) [![codecov](https://codecov.io/gh/nhamilakis/virtual-dataset/branch/master/graph/badge.svg?token=AH4C4YR7Q5)](https://codecov.io/gh/nhamilakis/virtual-dataset)

A small utility that allows to mount virtually a list of files as a folder.

# Installation 

Virtual-Dataset can be installed as a normal python package just run `pip install ...`

# Usage

There are two main functions `mount`, `umount`

**Mount:** allows creating the temporary mount with all the necessary files inside.

**Umount:** allows deletion of temporary mount folders


*Simple Example :* 

```python
from vdataset import mount, unmount

file_list = [ 'data/file1.txt', 'data/file2.txt', 'other_data/file6.txt', '/data/file.txt']
location = mount(file_list)

# location folder contains symlinks with all the files specified

# cleans up mount and removes all created files
unmount(location)
```

> All files are created as symbolic links to the originals so no data copy happens on mount


> unmount allows a safe option that when turned on will fail to delete the directory if any file in it is not a symlink

## Mount Input

Input can be of multiple format:

 - A simple list of files `List[Path, str]` that can be anywhere on your machine.
 - A dictionary allows preserving (or specifying) a file structure inside the created folder
ex:

```python
obj = {
    "dir1": ['file1.txt', 'file2.txt', 'file3.txt', 'file4.txt'],
    "dir2": ['file5.txt', 'file6.txt', 'file7.txt', 'file8.txt', 'file9.txt'],
    "dir3": {
        "subDir1": [
            'file10.txt',
            'file11.txt',
            'file12.txt',
            'file13.txt',
            'file14.txt',
            'file15.txt'
        ],
        "subDir2": 'file19.txt',
    },
    "dir4": ['file16.txt', 'file17.txt', 'file18.txt']
}
```

Creates the following temp folder : 

```
tmpdir
├── dir1
│   ├── file1.txt -> source_dir/file1.txt
│   ├── file2.txt -> source_dir/file2.txt
│   ├── file3.txt -> source_dir/file3.txt
│   └── file4.txt -> source_dir/file4.txt
├── dir2
│   ├── file5.txt -> source_dir/file5.txt
│   ├── file6.txt -> source_dir/file6.txt
│   ├── file7.txt -> source_dir/file7.txt
│   ├── file8.txt -> source_dir/file8.txt
│   └── file9.txt -> source_dir/file9.txt
├── dir3
│   ├── subDir1
│   │   ├── file10.txt -> source_dir/file10.txt
│   │   ├── file11.txt -> source_dir/file11.txt
│   │   ├── file12.txt -> source_dir/file12.txt
│   │   ├── file13.txt -> source_dir/file13.txt
│   │   ├── file14.txt -> source_dir/file14.txt
│   │   └── file15.txt -> source_dir/file15.txt
│   └── subDir2
│       └── file19.txt -> source_dir/file19.txt
└── dir4
    ├── file16.txt -> source_dir/file16.txt
    ├── file17.txt -> source_dir/file17.txt
    └── file18.txt -> source_dir/file18.txt

```


- Input can be taken from yaml or json files (using mount_from_index_file function)

- Input can also be another directory (using mount_from_location function)

## CLI

A command line utility exists to allow usage from outside python.

When installing the package the `vmount` command is installed in the current environment.

```bash
❯ vmount
usage: vmount [-h] [-u UMOUNT] [-i MOUNT_FROM_INDEX] [-d MOUNT_FROM_DIR] [--unsafe] [-k INDEX_KEY] [-t TMP_PREFIX] [-s KEEP_STRUCTURE] [-p PATTERN]

optional arguments:
  -h, --help            show this help message and exit
  -u UMOUNT, --umount UMOUNT
                        unmount location
  -i MOUNT_FROM_INDEX, --mount-from-index MOUNT_FROM_INDEX
                        mount from an index file [yaml, json]
  -d MOUNT_FROM_DIR, --mount-from-dir MOUNT_FROM_DIR
                        mount from a directory
  --unsafe              practice unsafe unmounting techniques (default: false)
  -k INDEX_KEY, --index-key INDEX_KEY
                        path to sub-item when loading index object (delimited by dots ex: key1.item3)
  -t TMP_PREFIX, --tmp-prefix TMP_PREFIX
                        Use this location as a prefix for creating mount point
  -s KEEP_STRUCTURE, --keep-structure KEEP_STRUCTURE
                        Keep directory structure when mounting from dir
  -p PATTERN, --pattern PATTERN
                        Pattern to match when mounting from dir (list)
```