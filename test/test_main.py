import os
import subprocess
import sys
import zipfile
from pathlib import Path

SCRIPT_NAME = "cbz-wrap.exe" if os.name == "nt" else "cbz-wrap"


def make_zip(path, entries):
    with zipfile.ZipFile(path, "w") as archive:
        for name, data in entries:
            archive.writestr(name, data)


def test_read_flag_resolves_relative_path_and_lists_files(tmp_path):
    archive = tmp_path / "pages.zip"
    make_zip(archive, [("001.jpg", b"one"), ("002.jpg", b"two")])

    result = subprocess.run(
        [sys.executable, "-m", "cbz_wrap", "-r", "pages.zip"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )

    assert str(archive) in result.stdout
    assert "001.jpg" in result.stdout
    assert "002.jpg" in result.stdout


def test_console_script_reads_files(tmp_path):
    archive = tmp_path / "pages.zip"
    make_zip(archive, [("001.jpg", b"one")])
    script = Path(sys.executable).with_name(SCRIPT_NAME)

    result = subprocess.run(
        [str(script), "-r", str(archive)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )

    assert "001.jpg" in result.stdout


def test_read_flag_discards_output_and_files_arguments(tmp_path):
    archive = tmp_path / "pages.zip"
    make_zip(archive, [("001.jpg", b"one")])
    ignored_output = tmp_path / "ignored.cbz"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "cbz_wrap",
            "-r",
            str(archive),
            "-o",
            str(ignored_output),
            "-f",
            str(tmp_path / "missing.cbz"),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )

    assert "001.jpg" in result.stdout
    assert not ignored_output.exists()


def test_output_and_files_compile_chapters(tmp_path):
    first = tmp_path / "Chapter 1.cbz"
    make_zip(first, [("nested/001.jpg", b"one")])
    second = tmp_path / "Chapter 2.cbz"
    make_zip(second, [("folder/002.webp", b"two")])
    compiled = tmp_path / "compiled.cbz"

    subprocess.run(
        [
            sys.executable,
            "-m",
            "cbz_wrap",
            "-o",
            "compiled.cbz",
            "-f",
            "Chapter 1.cbz",
            "Chapter 2.cbz",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )

    with zipfile.ZipFile(compiled) as archive:
        assert archive.namelist() == [
            "Chapter 1/001.jpg",
            "Chapter 2/002.webp",
        ]
        assert archive.read("Chapter 1/001.jpg") == b"one"
        assert archive.read("Chapter 2/002.webp") == b"two"


def test_simplify_flag_renames_chapters_and_pages(tmp_path):
    chapter = tmp_path / "Series Ch.01.cbz"
    make_zip(chapter, [("Series Ch.01/Series Ch.01-Pg18.jpg", b"eighteen")])
    compiled = tmp_path / "compiled.cbz"

    subprocess.run(
        [
            sys.executable,
            "-m",
            "cbz_wrap",
            "-o",
            "compiled.cbz",
            "-f",
            "Series Ch.01.cbz",
            "-s",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )

    with zipfile.ZipFile(compiled) as archive:
        assert archive.namelist() == ["Chapter 01/018.jpg"]
        assert archive.read("Chapter 01/018.jpg") == b"eighteen"


def test_no_arguments_prints_help():
    result = subprocess.run(
        [sys.executable, "-m", "cbz_wrap"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "usage:" in result.stdout
    assert "-r" in result.stdout
    assert "-o" in result.stdout
    assert "-f" in result.stdout
    assert "-s" in result.stdout


def test_output_requires_files():
    result = subprocess.run(
        [sys.executable, "-m", "cbz_wrap", "-o", "compiled.cbz"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "-f" in result.stderr


def test_files_require_output():
    result = subprocess.run(
        [sys.executable, "-m", "cbz_wrap", "-f", "chapter.cbz"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "-o" in result.stderr
