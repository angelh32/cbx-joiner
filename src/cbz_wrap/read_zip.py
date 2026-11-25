import re
import zipfile
from pathlib import Path, PurePosixPath

IMAGE_EXTENSIONS = {
    ".avif",
    ".bmp",
    ".gif",
    ".jpe",
    ".jpeg",
    ".jpg",
    ".png",
    ".tif",
    ".tiff",
    ".webp",
}

CHAPTER_PATTERN = re.compile(r"Ch(?:apter)?\.?\s*(\d+(?:\.\d+)?)", re.IGNORECASE)
PAGE_PATTERN = re.compile(r"Pg\.?\s*(\d+)", re.IGNORECASE)


def _simplify_chapter_folder(stem):
    """Return ``Chapter NN`` for a chapter-like stem, otherwise the stem."""
    match = CHAPTER_PATTERN.search(stem)
    if not match:
        return stem
    major, _, minor = match.group(1).partition(".")
    number = f"{int(major):02d}"
    if minor and int(minor) != 0:
        number += f".{int(minor)}"
    return f"Chapter {number}"


def _simplify_image_name(name):
    """Return ``NNN.ext`` for a page-like name, otherwise the original name."""
    path = PurePosixPath(name)
    match = PAGE_PATTERN.search(path.stem)
    if not match:
        return path.name
    return f"{int(match.group(1)):03d}{path.suffix}"


def _archive_files(archive):
    """Return archive entry names, excluding directory entries."""
    return [name for name in archive.namelist() if not name.endswith("/")]


def _build_tree(names):
    """Build a nested dictionary from archive entry paths."""
    tree = {}
    for name in names:
        parts = PurePosixPath(name).parts
        if not parts:
            continue
        node = tree
        for part in parts:
            node = node.setdefault(part, {})
    return tree


def _print_tree(tree, prefix=""):
    """Print a nested dictionary as a box-drawing tree."""
    entries = sorted(tree.items())
    last_index = len(entries) - 1
    for index, (name, children) in enumerate(entries):
        is_last = index == last_index
        connector = "└── " if is_last else "├── "
        print(f"{prefix}{connector}{name}")
        if children:
            _print_tree(children, prefix + ("    " if is_last else "│   "))


def read_zip(filename):
    """Print the archive contents as a tree and return the file names.

    Directory entries (names ending in ``/``) are excluded from the returned
    list, but are used to reconstruct the printed tree. ``filename`` may be a
    path string or a path-like object.
    """
    with zipfile.ZipFile(filename) as archive:
        list_of_files = _archive_files(archive)
        tree = _build_tree(archive.namelist())

    print(Path(filename).name)
    _print_tree(tree)
    return list_of_files


def create_zip(filename):
    """Create (or overwrite) an empty zip archive and return its path."""
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w"):
        pass

    print(path)
    return path


def add_files_from_chapters(compiled_zip, chapters, simplify=False):
    """Copy the images from each chapter archive into ``compiled_zip``.

    By default every chapter's images are placed in a folder named after that
    chapter's zip file (its stem, without the ``.zip``/``.cbz`` extension).
    When ``simplify`` is true, ``Series Ch.01/Series Ch.01-Pg18.jpg`` becomes
    ``Chapter 01/018.jpg``. Names without a recognizable ``Ch.`` or ``Pg.``
    number are left as-is.

    Original nested folders are discarded: images are stored directly in the
    chapter folder. Non-image files and directory entries are ignored. If two
    images end up with the same name, the later one gets ``_2``, ``_3``, etc.

    Returns the path to the compiled zip.
    """
    destination = create_zip(compiled_zip)
    used_names = set()

    with zipfile.ZipFile(destination, "a") as compiled:
        for chapter in chapters:
            chapter_path = Path(chapter)
            chapter_folder = (
                _simplify_chapter_folder(chapter_path.stem)
                if simplify
                else chapter_path.stem
            )

            with zipfile.ZipFile(chapter_path) as source:
                for name in _archive_files(source):
                    if PurePosixPath(name).suffix.lower() not in IMAGE_EXTENSIONS:
                        continue

                    image_name = (
                        _simplify_image_name(name)
                        if simplify
                        else PurePosixPath(name).name
                    )
                    arcname = f"{chapter_folder}/{image_name}"
                    if arcname in used_names:
                        stem = PurePosixPath(image_name).stem
                        suffix = PurePosixPath(image_name).suffix
                        counter = 2
                        while (
                            f"{chapter_folder}/{stem}_{counter}{suffix}"
                            in used_names
                        ):
                            counter += 1
                        arcname = f"{chapter_folder}/{stem}_{counter}{suffix}"

                    used_names.add(arcname)
                    compiled.writestr(arcname, source.read(name))

    return destination
