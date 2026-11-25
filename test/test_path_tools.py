import os

from cbz_wrap.path_tools import get_absolute_path


def test_relative_path_returns_absolute_path():
    result = get_absolute_path("some/file.txt")

    assert result == os.path.abspath("some/file.txt")
    assert os.path.isabs(result)


def test_absolute_path_is_unchanged():
    path = os.path.abspath("file.txt")

    assert get_absolute_path(path) == path


def test_normalizes_parent_segments():
    assert get_absolute_path("dir/../file.txt") == os.path.abspath("file.txt")


def test_prints_absolute_path(capsys):
    result = get_absolute_path("file.txt")

    assert capsys.readouterr().out.strip() == result
