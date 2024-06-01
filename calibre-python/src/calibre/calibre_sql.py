from pathlib import Path
from typing import List

from calibre.calibre_library import AbstractCalibreLibrary
from calibre.objects import (
    BookMetadata,
    InternalCalibreField,
    InternalBookMetadata,
)
from calibre.search_params import SearchParams
from calibre.converters import (
    book_metadata_internal_to_external,
    calibre_field_external_to_internals,
)
from calibre.metadata_db import MetadataDB
import sqlite3
import epub


class CalibreSql(AbstractCalibreLibrary):
    def __init__(self, library_path: Path):
        super().__init__(library_path=library_path)

        self.metadata_db = MetadataDB(self.library_path / "metadata.db")

    def _list_all_tables(self):
        cursor = self.connection.cursor()

        res = cursor.execute("SELECT * FROM sqlite_master WHERE type='table';")

        print(res.fetchall())

    def list_books(self, params: SearchParams = SearchParams()) -> List[BookMetadata]:
        cur = self.connection.cursor()
        fields = params.fields

        # Turn the list of public fields to the list of internal ones
        internal_fields = [InternalCalibreField.id, InternalCalibreField.title]
        for field in fields:
            internal_fields.extend(calibre_field_external_to_internals(field))

        # Remove potential duplicates
        internal_fields = list(set(internal_fields))

        query = "SELECT "
        first = True
        for internal_field in internal_fields:
            if first:
                query += f" {internal_field.value}"
                first = False
            else:
                query += f", {internal_field.value}"

        query += " FROM meta"

        if params.filters:
            for filter in params.filters:
                query += f" WHERE {filter.to_sql_filter()}"

        query += " ORDER BY id"

        res = cur.execute(query)
        res = res.fetchall()

        res_parsed = []
        for row in res:
            data = {}
            for idx, field in enumerate(internal_fields):
                data[field.value] = row[idx]
            internal_book_metadata = InternalBookMetadata.model_validate(data)

            book_metadata = book_metadata_internal_to_external(
                internal=internal_book_metadata,
                library_path=self.library_path,
                fields=fields,
            )

            res_parsed.append(book_metadata)

        return res_parsed

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
