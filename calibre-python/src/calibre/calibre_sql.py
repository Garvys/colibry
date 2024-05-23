from pathlib import Path
from typing import List, Optional

from calibre.calibre_library import CalibreLibrary
from calibre.objects import BookMetadata, CalibreField
import sqlite3

class Concatenate:
    '''String concatenation aggregator for sqlite'''

    def __init__(self, sep=','):
        self.sep = sep
        self.ans = []

    def step(self, value):
        if value is not None:
            self.ans.append(value)

    def finalize(self):
        try:
            if not self.ans:
                return None
            return self.sep.join(self.ans)
        except Exception:
            import traceback
            traceback.print_exc()
            raise

class SortedConcatenate:
    '''String concatenation aggregator for sqlite, sorted by supplied index'''
    sep = ','

    def __init__(self):
        self.ans = {}

    def step(self, ndx, value):
        if value is not None:
            self.ans[ndx] = value

    def finalize(self):
        try:
            if len(self.ans) == 0:
                return None
            return self.sep.join(map(self.ans.get, sorted(self.ans.keys())))
        except Exception:
            import traceback
            traceback.print_exc()
            raise


class CalibreSql(CalibreLibrary):
    def __init__(self, library_path: Path):
        super().__init__(library_path=library_path)

        self.connection = sqlite3.connect(self.library_path / "metadata.db")
        self.connection.create_aggregate('sortconcat', 2, SortedConcatenate)
        self.connection.create_aggregate('concat', 1, Concatenate)

    def _list_all_tables(self):
        cursor = self.connection.cursor()

        res = cursor.execute("SELECT * FROM sqlite_master WHERE type='table';")

        print(res.fetchall())

    def list(self, fields: List[CalibreField]) -> List[BookMetadata]:
        cur = self.connection.cursor()

        query = "SELECT id"
        for field in fields:
            if field == CalibreField.authors:
                query += ", authors"
            elif field == CalibreField.title:
                query += ", title"
            elif field == CalibreField.timestamp:
                query += ", books.timestamp"
            elif field == CalibreField.series_index:
                query += ", books.series_index"
            elif field == CalibreField.cover:
                query += ", books.path"
            elif field == CalibreField.series:
                query += ", series.name"
            elif field == CalibreField.formats:
                query += ", formats"
            else:
                raise ValueError(f"Field not supported : {field}")

        # query += " FROM books"
        # if CalibreField.authors in fields:
        #     query += (
        #         " LEFT JOIN books_authors_link on books.id = books_authors_link.book"
        #     )
        #     query += " LEFT JOIN authors on books_authors_link.author = authors.id"

        # if CalibreField.series in fields:
        #     query += (
        #         " LEFT JOIN books_series_link on books.id = books_series_link.book"
        #     )
        #     query += " LEFT JOIN series on books_series_link.series = series.id"

        # if CalibreField.formats in fields:
        #     query += (
        #         " LEFT JOIN data on books.id = data.book"
        #     )

        query += " FROM meta"

        query += " ORDER BY id"

        print(query)
        res = cur.execute(query)
        res = res.fetchall()
        print(res)

        res_parsed = []
        for row in res:
            data = {"id": row[0]}
            for idx, field in enumerate(fields):
                if field == CalibreField.cover:
                    v = row[idx+1]
                    if v:
                        v = self.library_path / v / "cover.jpg"
                        if not v.exists():
                            v = None
                    data["cover"] = v
                else:
                    data[field.value] = row[idx + 1]
            book_metadata = BookMetadata.model_validate(data)

            if book_metadata.timestamp is not None:
                # Remove microsecond to be aligned with calibredb
                book_metadata.timestamp = book_metadata.timestamp.replace(microsecond=0)

            res_parsed.append(book_metadata)

        return res_parsed
