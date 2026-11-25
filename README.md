# cbz-wrap

A small Python package with a command-line entry point and a pytest test suite.

## Layout

```
.
├── AGENTS.md                 # Instructions for coding agents
├── README.md                 # This file
├── pyproject.toml            # Project, build, console script, and pytest config
├── src/
│   └── cbz_wrap/
│       ├── __init__.py       # Package marker
│       ├── __main__.py       # Enables `python -m cbz_wrap`
│       ├── main.py           # CLI entry point
│       ├── path_tools.py     # Path helpers
│       └── read_zip.py       # Reading, creating, and compiling archives
├── test/                     # pytest suite
└── test-data/                # Sample CBZ fixtures
```

## Setup

Create and activate a virtual environment, then install the package in editable mode:

```sh
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

Activating the venv puts the `cbz-wrap` command on your `PATH`. If you prefer not to activate it, call `venv/bin/cbz-wrap ...` from the project directory instead. Re-run `pip install -e .` after changing `pyproject.toml`.

## Run the tests

With the venv activated:

```sh
python -m pytest
```

Or without activating it:

```sh
venv/bin/python -m pytest
```

## Use the CLI

With the venv activated, use `cbz-wrap` from any directory. Without activating, use `venv/bin/cbz-wrap` from the project directory. `python -m cbz_wrap` works either way.

List the files in one archive as a tree with `-r` (this ignores `-o`, `-f` and `-s`):

```sh
cbz-wrap -r "test-data/Kiss x Death/Kiss x Death Ch.01.0.cbz"
```

Example tree output:

```text
Kiss x Death Ch.25.0.cbz
└── Kiss x Death 25
    ├── Kiss-x-Death-25-Pg1.jpg
    ├── Kiss-x-Death-25-Pg2.jpg
    └── ...
```

Compile several chapters into one archive with `-o` and `-f`:

```sh
cbz-wrap -o compiled.cbz \
  -f "test-data/Kiss x Death/Kiss x Death Ch.25.0.cbz" \
     "test-data/Kiss x Death/Kiss x Death Ch.25.1.cbz"
```

`-f` takes space-separated file paths. `.cba`, `.cbz`, and `.zip` are all ZIP containers and work the same way.

Add `-s`/`--simplify` to rename chapters and pages while compiling. For example, `Series Ch.01/Series Ch.01-Pg18.jpg` becomes `Chapter 01/018.jpg`:

```sh
cbz-wrap -s -o compiled.cbz \
  -f "test-data/Kiss x Death/Kiss x Death Ch.25.0.cbz" \
     "test-data/Kiss x Death/Kiss x Death Ch.25.1.cbz"
```

During compilation only image files are copied (jpg/jpeg, png, webp, gif, bmp,
tif/tiff, avif). Nested folders from each chapter are flattened into one folder
named after that chapter's archive. If two images end up with the same name,
the later one gets `_2`, `_3`, and so on.

Running with no arguments prints the help text. Relative paths are resolved against the current working directory.
