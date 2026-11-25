# AGENTS.md

Instructions for AI coding agents working in this repository.

## Project overview

`cbz-wrap` is a small Python CLI for reading CBZ/CBA/ZIP archives and combining
several chapter archives into one compiled archive. It uses a `src/` package
layout, `argparse` for the CLI, and `pytest` for tests.

## Project structure

```text
.
├── AGENTS.md                 # This file
├── README.md                 # User-facing setup and CLI docs
├── pyproject.toml            # Project metadata, build, console script, pytest config
├── .gitignore
├── src/
│   └── cbz_wrap/             # Installable package (no top-level modules)
│       ├── __init__.py       # Package marker
│       ├── __main__.py       # Enables `python -m cbz_wrap`
│       ├── main.py           # CLI entry point
│       ├── path_tools.py     # Path helpers
│       └── read_zip.py       # Zip/CBZ reading, creation, and compilation
├── test/                     # pytest suite
│   ├── test_main.py
│   ├── test_path_tools.py
│   └── test_read_zip.py
├── test-data/                # Sample CBZ fixtures; treat as read-only
│   └── Kiss x Death/
└── venv/                     # Local virtual environment (not committed)
```

Generated and ignored: `src/cbz_wrap.egg-info/`, `__pycache__/`, `.pytest_cache/`.

## File responsibilities

- `src/cbz_wrap/main.py`: CLI with `-r/--read FILE`, `-o/--output FILE`,
  `-f/--files FILE [FILE ...]`, and `-s/--simplify`. `-r` takes precedence and
  ignores `-o`, `-f` and `-s`. Without `-r`, both `-o` and `-f` are required;
  `-s` passes `simplify=True` to `add_files_from_chapters`. No arguments prints
  help and exits 0. Paths are resolved with `get_absolute_path` before use.
- `src/cbz_wrap/path_tools.py`: `get_absolute_path(path)` prints and returns
  `os.path.abspath(path)`. The file does not need to exist.
- `src/cbz_wrap/read_zip.py`:
  - `read_zip(filename)` prints the archive basename as the root of an ASCII
    tree (entries sorted alphabetically) and returns a flat list of
    non-directory entry names.
  - `create_zip(filename)` creates/overwrites an empty archive, creates parent
    directories, prints, and returns a `Path`.
  - `add_files_from_chapters(compiled_zip, chapters, simplify=False)` calls
    `create_zip`, keeps only files with extensions in `IMAGE_EXTENSIONS`, and
    stores each image as `<chapter zip stem>/<image basename>`, flattening
    original nested folders. With `simplify=True`, `Series Ch.01-Pg18.jpg`
    becomes `018.jpg` in a `Chapter 01` folder; unmatched names are left alone.
    Duplicate image basenames within a chapter get `_2`, `_3`, etc.
- Tests import from `cbz_wrap` (for example `from cbz_wrap.read_zip import
  read_zip`), not from `src.cbz_wrap`.

## Commands

```sh
# One-time setup (or after changing pyproject.toml)
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -e ".[dev]"

# Tests
python -m pytest

# CLI
cbz-wrap -r "test-data/Kiss x Death/Kiss x Death Ch.01.0.cbz"
cbz-wrap -o compiled.cbz \
  -f "test-data/Kiss x Death/Kiss x Death Ch.25.0.cbz" \
     "test-data/Kiss x Death/Kiss x Death Ch.25.1.cbz"
cbz-wrap -s -o compiled.cbz \
  -f "test-data/Kiss x Death/Kiss x Death Ch.25.0.cbz" \
     "test-data/Kiss x Death/Kiss x Death Ch.25.1.cbz"
```

Without activating the venv, use `venv/bin/python -m pytest`,
`venv/bin/cbz-wrap ...`, or `venv/bin/python -m cbz_wrap ...`.

## Conventions and guardrails

- Keep importable code inside `src/cbz_wrap/`; do not add root-level scripts.
- Use relative imports inside the package (for example `from .read_zip import
  read_zip`).
- pytest has no `pythonpath` workaround: tests require the editable install.
- Preserve the existing print side effects in the helpers; CLI output and tests
  depend on them.
- Accept path strings and `pathlib.Path` objects in path-taking functions.
- ZIP entry names use forward slashes; use `pathlib.PurePosixPath` when
  parsing them.
- `.cba` and `.cbz` are ZIP containers, so extension should not affect reading.
- Treat `test-data/` as fixture data; do not modify or delete it.
- When changing behavior, update the matching tests and run the full suite.
