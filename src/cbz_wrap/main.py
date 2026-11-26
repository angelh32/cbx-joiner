"""Command-line entry point for reading or compiling zip/CBZ archives."""

import argparse

from .path_tools import get_absolute_path
from .read_zip import add_files_from_chapters, read_zip


def main():
    parser = argparse.ArgumentParser(
        description="Read a zip/CBZ archive, or compile chapter archives into one."
    )
    parser.add_argument(
        "-r",
        "--read",
        metavar="FILE",
        help="list the files inside a single archive (ignores -o, -f and -s)",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="FILE",
        help="path of the compiled archive to create",
    )
    parser.add_argument(
        "-f",
        "--files",
        nargs="+",
        metavar="FILE",
        help="chapter archives to copy into the compiled archive",
    )
    parser.add_argument(
        "-s",
        "--simplify",
        action="store_true",
        help="rename chapters/pages to 'NN-chapter/NNN.ext'",
    )
    args = parser.parse_args()

    if not (args.read or args.output or args.files):
        parser.print_help()
        return

    if args.read:
        absolute_path = get_absolute_path(args.read)
        read_zip(absolute_path)
        return

    if not args.output:
        parser.error("-o/--output is required unless -r/--read is given")
    if not args.files:
        parser.error("-f/--files is required unless -r/--read is given")

    output = get_absolute_path(args.output)
    chapters = [get_absolute_path(filename) for filename in args.files]
    add_files_from_chapters(output, chapters, simplify=args.simplify)


if __name__ == "__main__":
    main()
