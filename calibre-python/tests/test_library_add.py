from pathlib import Path
from typing import List
from calibre import CalibreSql, CalibreDB, CalibreField
import pytest


def test_library_add(tmp_path: Path, ebook_paths: List[Path]):
    ebook_paths = ebook_paths[:1]
    fields = [CalibreField.authors]

    library_calibredb = CalibreDB.new_empty_library(tmp_path / "library_db").add_books(ebooks=ebook_paths)
    books_metadata_db = library_calibredb.list_books(fields)
    print(books_metadata_db)

    library_sql = CalibreSql.new_empty_library(tmp_path / "library_sql").add_books(ebooks=ebook_paths)
    books_metadata_sql = library_sql.list_books(fields)


    assert len(books_metadata_db) == len(ebook_paths)
    assert len(books_metadata_sql) == len(ebook_paths)
    assert books_metadata_db == books_metadata_sql
