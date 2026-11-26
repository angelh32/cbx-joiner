import zipfile

from cbz_wrap.read_zip import (
    add_files_from_chapters,
    create_zip,
    read_zip,
)


def make_zip(path, entries):
    with zipfile.ZipFile(path, "w") as archive:
        for name, data in entries:
            archive.writestr(name, data)


def test_returns_file_names(tmp_path):
    archive = tmp_path / "pages.zip"
    make_zip(
        archive,
        [("001.jpg", b"one"), ("002.jpg", b"two"), ("003.jpg", b"three")],
    )

    assert read_zip(archive) == ["001.jpg", "002.jpg", "003.jpg"]


def test_skips_directory_entries(tmp_path):
    archive = tmp_path / "nested.zip"
    make_zip(
        archive,
        [
            ("sub/", b""),
            ("sub/001.jpg", b"one"),
            ("002.jpg", b"two"),
        ],
    )

    assert read_zip(archive) == ["sub/001.jpg", "002.jpg"]


def test_empty_archive(tmp_path):
    archive = tmp_path / "empty.zip"
    make_zip(archive, [])

    assert read_zip(archive) == []


def test_prints_file_list_as_tree(tmp_path, capsys):
    archive = tmp_path / "pages.zip"
    make_zip(archive, [("001.jpg", b"one")])

    read_zip(archive)

    assert capsys.readouterr().out.strip() == (
        "pages.zip\n"
        "└── 001.jpg"
    )


def test_prints_nested_folders_as_tree(tmp_path, capsys):
    archive = tmp_path / "nested.zip"
    make_zip(
        archive,
        [
            ("sub/", b""),
            ("sub/001.jpg", b"one"),
            ("002.jpg", b"two"),
            ("deep/inner/003.webp", b"three"),
        ],
    )

    read_zip(archive)

    assert capsys.readouterr().out.strip() == (
        "nested.zip\n"
        "├── 002.jpg\n"
        "├── deep\n"
        "│   └── inner\n"
        "│       └── 003.webp\n"
        "└── sub\n"
        "    └── 001.jpg"
    )


def test_create_zip_creates_empty_archive(tmp_path):
    target = tmp_path / "output" / "compiled.cbz"

    result = create_zip(target)

    assert result == target
    with zipfile.ZipFile(target) as archive:
        assert archive.namelist() == []


def test_create_zip_overwrites_existing_archive(tmp_path):
    target = tmp_path / "compiled.cbz"
    make_zip(target, [("old.jpg", b"old")])

    create_zip(target)

    with zipfile.ZipFile(target) as archive:
        assert archive.namelist() == []


def test_add_files_from_chapters_flattens_nested_images(tmp_path):
    first = tmp_path / "Chapter 1.cbz"
    make_zip(
        first,
        [
            ("Chapter 1/", b""),
            ("Chapter 1/001.jpg", b"one"),
            ("Chapter 1/sub/002.webp", b"two"),
            ("notes.txt", b"ignore me"),
        ],
    )
    second = tmp_path / "Chapter 2.zip"
    make_zip(
        second,
        [
            ("nested/deeper/003.PNG", b"three"),
            ("004.jpeg", b"four"),
        ],
    )
    compiled = tmp_path / "compiled.cbz"

    result = add_files_from_chapters(compiled, [first, second])

    assert result == compiled
    with zipfile.ZipFile(compiled) as archive:
        assert archive.namelist() == [
            "Chapter 1/001.jpg",
            "Chapter 1/002.webp",
            "Chapter 2/003.PNG",
            "Chapter 2/004.jpeg",
        ]
        assert archive.read("Chapter 1/001.jpg") == b"one"
        assert archive.read("Chapter 1/002.webp") == b"two"
        assert archive.read("Chapter 2/003.PNG") == b"three"
        assert archive.read("Chapter 2/004.jpeg") == b"four"


def test_add_files_from_chapters_disambiguates_duplicate_names(tmp_path):
    chapter = tmp_path / "Ch.cbz"
    make_zip(chapter, [("a/001.jpg", b"first"), ("b/001.jpg", b"second")])
    compiled = tmp_path / "compiled.cbz"

    add_files_from_chapters(compiled, [chapter])

    with zipfile.ZipFile(compiled) as archive:
        assert archive.namelist() == ["Ch/001.jpg", "Ch/001_2.jpg"]
        assert archive.read("Ch/001.jpg") == b"first"
        assert archive.read("Ch/001_2.jpg") == b"second"


def test_simplify_renames_folder_and_pages(tmp_path):
    chapter = tmp_path / "Series Ch.01.cbz"
    make_zip(
        chapter,
        [
            ("Series Ch.01/Series Ch.01-Pg18.jpg", b"eighteen"),
            ("Series Ch.01/Series Ch.01-Pg7.png", b"seven"),
        ],
    )
    compiled = tmp_path / "compiled.cbz"

    add_files_from_chapters(compiled, [chapter], simplify=True)

    with zipfile.ZipFile(compiled) as archive:
        assert archive.namelist() == [
            "01-chapter/018.jpg",
            "01-chapter/007.png",
        ]
        assert archive.read("01-chapter/018.jpg") == b"eighteen"
        assert archive.read("01-chapter/007.png") == b"seven"


def test_simplify_handles_decimals_and_keeps_unmatched_names(tmp_path):
    chapter = tmp_path / "Series Ch.25.0.cbz"
    make_zip(
        chapter,
        [
            ("Series 25/Series-25-Pg1.jpg", b"one"),
            ("cover.jpg", b"cover"),
        ],
    )
    misc = tmp_path / "Misc.cbz"
    make_zip(misc, [("misc/001.jpg", b"misc")])
    compiled = tmp_path / "compiled.cbz"

    add_files_from_chapters(compiled, [chapter, misc], simplify=True)

    with zipfile.ZipFile(compiled) as archive:
        assert archive.namelist() == [
            "25.0-chapter/001.jpg",
            "25.0-chapter/cover.jpg",
            "Misc/001.jpg",
        ]
        assert archive.read("25.0-chapter/001.jpg") == b"one"
        assert archive.read("Misc/001.jpg") == b"misc"
