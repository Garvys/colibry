from pathlib import Path
from typing import List

from calibre.calibre_library import AbstractCalibreLibrary
from calibre.objects import ExternalBookMetadata

from calibre.metadata_db import MetadataDB
import sqlite3
import epub
import shutil
import os
from unidecode import unidecode

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

            size = 0
            formats = []
            for d in b.data:
                if not b.book.path:
                    raise RuntimeError(f"Data provided without path for book : {b}")

                file_path = (
                    library_abs_path / b.book.path / f"{d.name}.{d.format.lower()}"
                )

                if not file_path.exists():
                    raise RuntimeError(f"File is missing : {file_path}")

                formats.append(file_path)
                size = max(size, d.uncompressed_size)

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
                    formats=formats,
                    last_modified=b.book.last_modified,
                    size=size,
                )
            )

        return res

    def add_book(self, ebook_path: Path):

        if not ebook_path.exists():
            raise RuntimeError(f"Can't add an ebook if it doesn't exist : {ebook_path}")

        book = epub.open_epub(ebook_path)
        title = ""
        titles = book.opf.metadata.titles
        if titles:
            title = titles[0][0]

        authors = []
        for c in book.opf.metadata.creators:
            name = c[0]
            sort = c[2]
            authors.append((name, sort))

        # Add metadata for book
        book_id = self.metadata_db.add_book(title=title, authors=authors)

        # Create folders
        author_folder = self.library_path / unidecode(authors[0][0])
        author_folder.mkdir(exist_ok=True)

        book_folder = author_folder / f"{title} ({book_id})"
        book_folder.mkdir()

        # Copy ebook
        book_filename = unidecode(f"{title} - {authors[0][0]}")
        shutil.copy(ebook_path, book_folder / f"{book_filename}.epub")

        with (book_folder / "metadata.opf").open(mode="w") as f:
            book.opf.metadata.as_xml_element().writexml(f)

        # Add ebook info to data table
        self.metadata_db.add_to_data_table(
            book_id=book_id,
            format="epub",
            name=book_filename,
            uncompressed_size=os.stat(ebook_path).st_size,
        )

        # Update path
        self.metadata_db.update_book_table(book_id=book_id, path=str(book_folder))

    def add_books(self, ebooks: List[Path]):
        for ebook in ebooks:
            self.add_book(ebook)
        return self
