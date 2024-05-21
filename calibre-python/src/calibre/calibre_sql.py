from pathlib import Path
from typing import List, Optional

from calibre.calibre_library import CalibreLibrary
from calibre.objects import BookMetadata
import sqlite3


class CalibreSql(CalibreLibrary):
    def __init__(self, library_path: Path):
        super().__init__(library_path=library_path)

    def _list_all_tables(self):
        connection = sqlite3.connect(self.library_path / "metadata.db")
        cursor = connection.cursor()

        res = cursor.execute("SELECT * FROM sqlite_master WHERE type='table';")

        print(res.fetchall())

    def list(
        self,
        limit: Optional[int] = None,
        sort_by: Optional[str] = None,
        ascending: bool = False,
        search: str = "",
    ) -> List[BookMetadata]:
        connection = sqlite3.connect(self.library_path / "metadata.db")
        cur = connection.cursor()
        res = cur.execute("SELECT title FROM books")
        res = res.fetchall()
        print(res)
        return [BookMetadata(title=e[0]) for e in res]
