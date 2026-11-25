import os


def get_absolute_path(path):
    """Print and return the absolute path for ``path``.

    Relative paths are resolved from the current working directory. Absolute
    paths are kept as-is, with any ``.`` or ``..`` segments normalized. The
    file itself does not need to exist.
    """
    absolute_path = os.path.abspath(path)
    print(absolute_path)
    return absolute_path
