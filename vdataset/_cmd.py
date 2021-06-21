#  Copyright (c) 2021.  Nicolas Hamilakis

import argparse
import sys
from pathlib import Path

from ._mount_samples import mount_from_location, mount_from_index_file
from ._core import unmount


def argument_parser():
    """ Builds argument parser """
    parser = argparse.ArgumentParser()

    # actions
    parser.add_argument("-u", "--umount", type=str, help="unmount location")
    parser.add_argument("-i", "--mount-from-index", type=str, help="mount from an index file [yaml, json]")
    parser.add_argument("-d", "--mount-from-dir", type=str, help="mount from a directory")

    # extra options
    parser.add_argument("--unsafe", action='store_true', help="practice unsafe unmounting techniques (default: false)")
    parser.add_argument("-k", "--index-key", type=str,
                        help="path to sub-item when loading index object (delimited by dots ex: key1.item3)")
    parser.add_argument("-t", "--tmp-prefix", type=str, help="Use this location as a prefix for creating mount point")
    parser.add_argument("-s", "--keep-structure", type=str, help="Keep directory structure when mounting from dir")
    parser.add_argument("-p", "--pattern", action="append", help="Pattern to match when mounting from dir (list)")

    return parser


def main(argv=None):
    """ CLI entry point """
    parser = argument_parser()

    if argv:
        args = parser.parse_args(argv)
    else:
        args = parser.parse_args()

    if args.umount:
        unmount(args.umount, safe=not args.unsafe)
        print(f"successfully unmounted {args.umount}")

    elif args.mount_from_index:
        mount_index_file = Path(args.mount_from_index)
        location = mount_from_index_file(mount_index_file, key=args.index_key, tmp_prefix=args.tmp_prefix)
        print(f"{location}")

    elif args.mount_from_dir:
        location = mount_from_location(
            args.mount_from_dir, keep_structure=args.keep_structure, file_regexp=args.pattern)
        print(f"{location}")

    else:
        parser.print_help()
        sys.exit(0)
