from pathlib import Path
from typing import List

from calibre.calibre_library import AbstractCalibreLibrary
from calibre.objects import ExternalBookMetadata

from calibre.metadata_db import MetadataDB
import sqlite3
import epub

COVER_FILENAME = "cover.jpg"


class CalibreSql(AbstractCalibreLibrary):
    def __init__(self, library_path: Path):
        super().__init__(library_path=library_path)

        self.metadata_db = MetadataDB(self.library_path / "metadata.db")

    def _list_all_tables(self):
        cursor = self.connection.cursor()

        res = cursor.execute("SELECT * FROM sqlite_master WHERE type='table';")

        print(res.fetchall())

    def list_books(self) -> List[ExternalBookMetadata]:
        book_aggregated_metadatas = self.metadata_db.list_books_from_meta_table()

        library_abs_path = self.library_path.absolute()

        res = []
        for b in book_aggregated_metadatas:
            # TODO: There is a field has_cover in the metadata.db that we could leverage here
            cover_path = library_abs_path / b.path / COVER_FILENAME
            cover = None
            if cover_path.exists():
                cover = cover_path

            res.append(
                ExternalBookMetadata(
                    id=b.id,
                    title=b.title,
                    authors=b.authors,
                    series=b.series,
                    series_index=b.series_index,
                    isbn=b.isbn,
                    author_sort=b.author_sort,
                    timestamp=b.timestamp,
                    pubdate=b.pubdate,
                    cover=cover,
                )
            )

        return res

    def add_book(self, ebook_path: Path):
        import epub

        if not ebook_path.exists():
            raise RuntimeError(f"Can't add an ebook if it doesn't exist : {ebook_path}")

        book = epub.open_epub(ebook_path)
        print(book.opf.metadata.titles)
        print(book.opf.metadata.creators)

    def add_books(self, ebooks: List[Path]):
        for ebook in ebooks:
            self.add_book(ebook)
        return self
