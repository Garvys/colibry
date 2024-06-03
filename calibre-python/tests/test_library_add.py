from pathlib import Path
from typing import List
from calibre import CalibreSql, CalibreDB


def files_in_library(library_path: Path) -> List[Path]:
    return sorted([str(e.relative_to(library_path)) for e in library_path.glob("**/*")])


def asset_eq_library(library_path_1: Path, library_path_2: Path):
    files_library_1 = files_in_library(library_path_1)
    files_library_2 = files_in_library(library_path_2)
    assert files_library_1 == files_library_2

    for f in files_library_1:
        if f.endswith(".opf"):
            assert (library_path_1 / f).read_text() == (library_path_2 / f).read_text()

    assert (
        CalibreDB(library_path_1).list_books() == CalibreDB(library_path_2).list_books()
    )

    assert (
        CalibreSql(library_path_1).list_books()
        == CalibreSql(library_path_2).list_books()
    )
    assert (
        CalibreSql(library_path_1).metadata_db.list_authors_from_authors_table()
        == CalibreSql(library_path_1).metadata_db.list_authors_from_authors_table()
    )
    assert (
        CalibreSql(library_path_1).metadata_db.list_series_from_series_table()
        == CalibreSql(library_path_1).metadata_db.list_series_from_series_table()
    )
    assert (
        CalibreSql(library_path_1).metadata_db.list_book_authors_links()
        == CalibreSql(library_path_1).metadata_db.list_book_authors_links()
    )
    assert (
        CalibreSql(library_path_1).metadata_db.list_book_series_link()
        == CalibreSql(library_path_1).metadata_db.list_book_series_link()
    )
    assert (
        CalibreSql(library_path_1).metadata_db.lists_books_from_books_table()
        == CalibreSql(library_path_1).metadata_db.lists_books_from_books_table()
    )
    assert (
        CalibreSql(library_path_1).metadata_db.list_data_table()
        == CalibreSql(library_path_1).metadata_db.list_data_table()
    )


def test_library_add(tmp_path: Path, ebook_paths: List[Path]):
    ebook_paths = [ebook_paths[-1]]

    library_calibredb = CalibreDB.new_empty_library(tmp_path / "library_db").add_books(
        ebooks=ebook_paths
    )

    library_sql = CalibreSql.new_empty_library(tmp_path / "library_sql").add_books(
        ebooks=ebook_paths
    )

    asset_eq_library(
        library_path_1=library_calibredb.library_path,
        library_path_2=library_sql.library_path
    )

