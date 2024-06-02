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
        book_structured_metadatas = self.metadata_db.list_books_structured()

        library_abs_path = self.library_path.absolute()

        res = []
        for b in book_structured_metadatas:
            authors = " & ".join([a.name for a in b.authors])

            cover = None
            if b.book.has_cover:
                cover = library_abs_path / b.book.path / COVER_FILENAME
                if not cover.exists():
                    raise RuntimeError(
                        f"Book is said to have a cover and it doesn't exist: {cover}"
                    )

            res.append(
                ExternalBookMetadata(
                    id=b.book.id,
                    title=b.book.title,
                    authors=authors,
                    series=b.serie.name if b.serie is not None else None,
                    series_index=b.book.series_index,
                    isbn=b.book.isbn,
                    author_sort=b.book.author_sort,
                    timestamp=b.book.timestamp,
                    pubdate=b.book.pubdate,
                    cover=cover,
                    formats=[],
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
