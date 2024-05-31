from pathlib import Path
import shutil
import sqlite3
from pydantic import BaseModel
from typing import Optional, List, Callable, Any
from calibre.sql_aggregators import title_sort


class AuthorMetadata(BaseModel):
    id: int
    name: str
    sort: str


class SerieMetadata(BaseModel):
    id: int
    name: str
    sort: str


class BookAuthorsLinkMetadata(BaseModel):
    id: int
    book: int
    authors: int


class MetadataDB:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)
        self.connection.create_function("title_sort", 1, title_sort)

    @classmethod
    def new_empty_db(cls, new_db_path: Path):
        path_empty_library = Path(__file__).resolve().parent / "empty_library"
        path_empty_db = path_empty_library / "metadata.db"
        shutil.copy(path_empty_db, new_db_path)
        return cls(new_db_path)

    def _list_table(
        self,
        table_name: str,
        fields: List[str],
        parser: Callable[[List[Any]], BaseModel],
    ) -> List[BaseModel]:
        cursor = self.connection.cursor()
        res = cursor.execute(f"SELECT {', '.join(fields)} FROM {table_name}")
        res = res.fetchall()
        res_parsed = []
        for e in res:
            res_parsed.append(parser(e))
        return res_parsed

    def _insert_in_table(self, table_name: str, fields: List[str], values: List[str]):
        if len(fields) != len(values):
            raise RuntimeError(
                f"Different number of fields and values: {fields} and {values}"
            )
        cursor = self.connection.cursor()
        fields_str = ", ".join(fields)
        values_str = ", ".join(f"'{e}'" for e in values)
        cursor.execute(
            f"INSERT OR IGNORE INTO {table_name} ({fields_str}) VALUES ({values_str})"
        )

    def list_authors_from_authors_table(self) -> List[AuthorMetadata]:
        return self._list_table(
            "authors",
            ["id", "name", "sort"],
            lambda x: AuthorMetadata(id=x[0], name=x[1], sort=x[2]),
        )

    def add_author_to_authors_table(self, name: str, sort: str):
        self._insert_in_table(
            table_name="authors", fields=["name", "sort"], values=[name, sort]
        )

    def get_author_id(self, name: str) -> Optional[int]:
        cursor = self.connection.cursor()
        res = cursor.execute(f"SELECT id FROM authors where name = '{name}'")
        author_id = res.fetchone()
        return author_id[0] if author_id is not None else None

    def list_series_from_series_table(self) -> List[SerieMetadata]:
        return self._list_table(
            "series",
            ["id", "name", "sort"],
            lambda x: SerieMetadata(id=x[0], name=x[1], sort=x[2]),
        )

    def add_serie_to_series_table(self, name: str, sort: str):
        self._insert_in_table(
            table_name="series", fields=["name", "sort"], values=[name, sort]
        )

    def get_serie_id(self, name: str) -> Optional[int]:
        cursor = self.connection.cursor()
        res = cursor.execute(f"SELECT id FROM series where name = '{name}'")
        serie_id = res.fetchone()
        return serie_id[0] if serie_id is not None else None

    # def list_book_authors_link(self):
