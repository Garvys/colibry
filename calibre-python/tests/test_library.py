from calibre.calibredb import CalibreDB
from calibre.calibre_sql import CalibreSql
from calibre.objects import CalibreField
from pathlib import Path
from typing import List


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

    assert len(library1.list()) == 0
    assert len(library2.list()) == len(ebook_paths)


def test_new_add_list_sql(tmp_path: Path, ebook_paths: List[Path]):
    library = CalibreDB.new_empty_library(tmp_path / "library").add(ebooks=ebook_paths)

    fields = [CalibreField.title]

    books_metadata_expected = library.list(fields=fields)

    library_sql = CalibreSql(library_path=library.library_path)

    # library_sql._list_all_tables()

    books_metadata = library_sql.list()

    assert books_metadata_expected == books_metadata
