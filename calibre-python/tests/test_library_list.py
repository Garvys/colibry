from pathlib import Path
from typing import List

import pytest
from calibre.calibre_sql import CalibreSql
from calibre.calibredb import CalibreDB


# def test_remove_books(tmp_path: Path, ebook_paths: List[Path]):
#     library = CalibreDB.new_empty_library(tmp_path / "library").add(ebooks=ebook_paths)

#     books_metadata = library.list_books()

#     library.remove_books(books_metadata[:2])

#     assert len(library.list_books()) == len(ebook_paths) - 2


# def test_remove_from_ids(tmp_path: Path, ebook_paths: List[Path]):
#     library = CalibreDB.new_empty_library(tmp_path / "library").add(ebooks=ebook_paths)

#     books_metadata = library.list_books()

#     library.remove_from_ids([e.id for e in books_metadata][:2])

#     assert len(library.list_books()) == len(ebook_paths) - 2


def test_list_books(
    library_calibredb: CalibreDB,
    library_calibresql: CalibreSql,
):
    books_metadata_expected = library_calibredb.list_books()
    books_metadata_expected = [
        b.model_copy_and_remove_microseconds() for b in books_metadata_expected
    ]

    books_metadata = library_calibresql.list_books()
    books_metadata = [b.model_copy_and_remove_microseconds() for b in books_metadata]

    print(books_metadata_expected[0])

    assert (
        books_metadata_expected == books_metadata
    ), f"calibreDB = {books_metadata_expected} calibresql {books_metadata}"
