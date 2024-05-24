from pathlib import Path
from typing import List

from calibre.calibre_library import CalibreLibrary
from calibre.objects import (
    BookMetadata,
    CalibreField,
    InternalCalibreField,
    InternalBookMetadata,
    calibre_field_external_to_internals,
    book_metadata_internal_to_external,
)
import sqlite3


class Concatenate:
    """String concatenation aggregator for sqlite"""

    def __init__(self, sep=","):
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
    """String concatenation aggregator for sqlite, sorted by supplied index"""

    sep = " & "

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
        self.connection.create_aggregate("sortconcat", 2, SortedConcatenate)
        self.connection.create_aggregate("concat", 1, Concatenate)

    def _list_all_tables(self):
        cursor = self.connection.cursor()

        res = cursor.execute("SELECT * FROM sqlite_master WHERE type='table';")

        print(res.fetchall())

    def list_books(self, fields: List[CalibreField]) -> List[BookMetadata]:
        cur = self.connection.cursor()

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

        query += " ORDER BY id"

        print(query)
        res = cur.execute(query)
        res = res.fetchall()
        print(res)

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
