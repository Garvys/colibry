from pathlib import Path
from typing import List, Optional

from calibre.calibre_library import CalibreLibrary
from calibre.objects import BookMetadata, CalibreField
import sqlite3


class CalibreSql(CalibreLibrary):
    def __init__(self, library_path: Path):
        super().__init__(library_path=library_path)

        self.connection = sqlite3.connect(self.library_path / "metadata.db")

    def _list_all_tables(self):
        cursor = self.connection.cursor()

        res = cursor.execute("SELECT * FROM sqlite_master WHERE type='table';")

        print(res.fetchall())

    def list(self, fields: List[CalibreField]) -> List[BookMetadata]:
        cur = self.connection.cursor()

        query = "SELECT books.id"
        for field in fields:
            if field == CalibreField.authors:
                query += ", authors.name"
            elif field == CalibreField.title:
                query += ", books.title"
            else:
                raise ValueError(f"Field not supported : {field}")

        query += " FROM books"
        if CalibreField.authors in fields:
            query += (
                " LEFT JOIN books_authors_link on books.id = books_authors_link.book"
            )
            query += " LEFT JOIN authors on books_authors_link.author = authors.id"

        query += " ORDER BY books.id"

        print(query)
        res = cur.execute(query)
        res = res.fetchall()
        print(res)

        res_parsed = []
        for row in res:
            data = {"id": row[0]}
            for idx, field in enumerate(fields):
                data[field.value] = row[idx + 1]
            res_parsed.append(BookMetadata.model_validate(data))

        return res_parsed
