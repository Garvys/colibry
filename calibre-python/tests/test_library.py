from pathlib import Path
from typing import List

import pytest
from calibre.calibre_sql import CalibreSql
from calibre.calibredb import CalibreDB
from calibre.objects import CalibreField


def test_new_add_list(tmp_path: Path, ebook_paths: List[Path]):
    library = CalibreDB.new_empty_library(tmp_path / "library").add(ebooks=ebook_paths)
    books_metadata = library.list()

    assert len(books_metadata) == len(ebook_paths)

    books_metadata = library.list(limit=1)

    assert len(books_metadata) == 1

    authors = library.list_authors()
    books_metadata = library.list(search=f'author:"{authors[0]}"')
    assert len(books_metadata) == 1
    assert books_metadata[0].authors == authors[0]


def test_remove_books(tmp_path: Path, ebook_paths: List[Path]):
    library = CalibreDB.new_empty_library(tmp_path / "library").add(ebooks=ebook_paths)

    books_metadata = library.list()

    library.remove_books(books_metadata[:2])

    assert len(library.list()) == len(ebook_paths) - 2


def test_remove_from_ids(tmp_path: Path, ebook_paths: List[Path]):
    library = CalibreDB.new_empty_library(tmp_path / "library").add(ebooks=ebook_paths)

    books_metadata = library.list()

    library.remove_from_ids([e.id for e in books_metadata][:2])

    assert len(library.list()) == len(ebook_paths) - 2


def test_clone(tmp_path: Path, ebook_paths: List[Path]):
    library1 = CalibreDB.new_empty_library(tmp_path / "library1")

    library2 = library1.clone(tmp_path / "library2").add(ebook_paths)

    assert len(library1.list_books()) == 0
    assert len(library2.list()) == len(ebook_paths)


@pytest.fixture(scope="session")
def library_calibredb(ebook_paths: List[Path]):
    from tempfile import TemporaryDirectory

    tmp = TemporaryDirectory()

    db = CalibreDB.new_empty_library(Path(tmp.name) / "library").add(ebooks=ebook_paths)
    # Attach tmp so that it gets removed when the db is destroyed
    db.tmp = tmp
    return db


@pytest.fixture(scope="session")
def library_calibresql(library_calibredb):
    return CalibreSql(library_path=library_calibredb.library_path)


@pytest.mark.parametrize(
    "fields",
    [
        [],
        [CalibreField.authors],
        [CalibreField.timestamp],
        [CalibreField.series_index],
        [CalibreField.cover],
        [CalibreField.series],
        [CalibreField.formats],
    ],
)
def test_new_add_list_sql(
    library_calibredb: CalibreDB,
    library_calibresql: CalibreSql,
    fields: List[CalibreField],
):
    books_metadata_expected = library_calibredb.list_books(fields=fields)

    books_metadata = library_calibresql.list_books(fields=fields)

    assert (
        books_metadata_expected == books_metadata
    ), f"calibreDB = {books_metadata_expected} calibresql {books_metadata}"
