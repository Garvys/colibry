from pathlib import Path
import shutil
import sqlite3
from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Callable, Any
from calibre.sql_aggregators import title_sort
from enum import Enum
from datetime import datetime
import uuid


class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AuthorMetadata(StrictBaseModel):
    id: int
    name: str
    sort: str


class SerieMetadata(StrictBaseModel):
    id: int
    name: str
    sort: str


class BookMetadata(StrictBaseModel):
    id: int
    title: str
    sort: str
    author_sort: Optional[str]
    series_index: int
    path: str
    has_cover: bool
    timestamp: datetime
    pubdate: datetime
    last_modified: datetime
    isbn: str
    lccn: str


class BookAuthorLinkMetadata(StrictBaseModel):
    id: int
    book_id: int
    author_id: int


class BookSerieLinkMetadata(StrictBaseModel):
    id: int
    book_id: int
    serie_id: int


class TableName(str, Enum):
    authors = "authors"
    series = "series"
    books = "books"
    books_authors_link = "books_authors_link"
    books_series_link = "books_series_link"


class MetadataDB:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)
        self.connection.create_function("title_sort", 1, title_sort)
        self.connection.create_function("uuid4", 0, lambda: str(uuid.uuid4()))

    @classmethod
    def new_empty_db(cls, new_db_path: Path):
        path_empty_library = Path(__file__).resolve().parent / "empty_library"
        path_empty_db = path_empty_library / "metadata.db"
        shutil.copy(path_empty_db, new_db_path)
        return cls(new_db_path)

    def _list_table(
        self,
        table_name: TableName,
        fields: List[str],
        parser: Callable[[List[Any]], BaseModel],
    ) -> List[BaseModel]:
        cursor = self.connection.cursor()
        res = cursor.execute(f"SELECT {', '.join(fields)} FROM {str(table_name.value)}")
        res = res.fetchall()
        res_parsed = []
        for e in res:
            res_parsed.append(parser(e))
        return res_parsed

    def _insert_in_table(
        self, table_name: TableName, fields: List[str], values: List[str]
    ):
        if len(fields) != len(values):
            raise RuntimeError(
                f"Different number of fields and values: {fields} and {values}"
            )
        cursor = self.connection.cursor()
        fields_str = ", ".join(fields)
        values_str = ", ".join(f"'{e}'" for e in values)
        cursor.execute(
            f"INSERT OR IGNORE INTO {str(table_name.value)} ({fields_str}) VALUES ({values_str})"
        )

    def _get_id_from_field(
        self, table_name: TableName, field_name: str, value: str
    ) -> Optional[int]:
        cursor = self.connection.cursor()
        res = cursor.execute(
            f"SELECT id FROM {str(table_name.value)} where {field_name} = '{value}'"
        )
        author_id = res.fetchone()
        return author_id[0] if author_id is not None else None

    def _update_table(
        self, table_name: TableName, id: int, fields: List[str], values: List[str]
    ):
        if not fields and not values:
            return

        if len(fields) != len(values):
            raise RuntimeError(
                f"Different number of fields and values: {fields} and {values}"
            )
        cursor = self.connection.cursor()
        setter = ", ".join(
            f"{field} = '{value}'" for field, value in zip(fields, values)
        )
        cursor.execute(f"UPDATE {str(table_name.value)} SET {setter} WHERE id = {id}")

    def list_authors_from_authors_table(self) -> List[AuthorMetadata]:
        return self._list_table(
            TableName.authors,
            ["id", "name", "sort"],
            lambda x: AuthorMetadata(id=x[0], name=x[1], sort=x[2]),
        )

    def add_author_to_authors_table(self, name: str, sort: str):
        self._insert_in_table(
            table_name=TableName.authors, fields=["name", "sort"], values=[name, sort]
        )

    def get_author_id(self, name: str) -> Optional[int]:
        return self._get_id_from_field(
            table_name=TableName.authors, field_name="name", value=name
        )

    def update_author_in_authors_table(
        self, id: int, name: Optional[str] = None, sort: Optional[str] = None
    ):
        fields = []
        values = []

        if name is not None:
            fields.append("name")
            values.append(name)

        if sort is not None:
            fields.append("sort")
            values.append(sort)

        self._update_table(
            table_name=TableName.authors, id=id, fields=fields, values=values
        )

    def list_series_from_series_table(self) -> List[SerieMetadata]:
        return self._list_table(
            TableName.series,
            ["id", "name", "sort"],
            lambda x: SerieMetadata(id=x[0], name=x[1], sort=x[2]),
        )

    def add_serie_to_series_table(self, name: str, sort: str):
        self._insert_in_table(
            table_name=TableName.series, fields=["name", "sort"], values=[name, sort]
        )

    def get_serie_id(self, name: str) -> Optional[int]:
        return self._get_id_from_field(
            table_name=TableName.series, field_name="name", value=name
        )

    def list_book_authors_link(self) -> List[BookAuthorLinkMetadata]:
        return self._list_table(
            table_name=TableName.books_authors_link,
            fields=["id", "book", "author"],
            parser=lambda x: BookAuthorLinkMetadata(
                id=x[0], book_id=x[1], author_id=x[2]
            ),
        )

    def add_book_author_link(self, book_id: int, author_id: int):
        self._insert_in_table(
            table_name=TableName.books_authors_link,
            fields=["book", "author"],
            values=[book_id, author_id],
        )

    def list_book_series_link(self) -> List[BookSerieLinkMetadata]:
        return self._list_table(
            table_name=TableName.books_series_link,
            fields=["id", "book", "series"],
            parser=lambda x: BookSerieLinkMetadata(
                id=x[0], book_id=x[1], serie_id=x[2]
            ),
        )

    def add_book_serie_link(self, book_id: int, serie_id: int):
        self._insert_in_table(
            table_name=TableName.books_series_link,
            fields=["book", "series"],
            values=[book_id, serie_id],
        )

    def lists_books_from_books_table(self):
        return self._list_table(
            table_name=TableName.books,
            fields=[
                "id",
                "title",
                "sort",
                "author_sort",
                "series_index",
                "has_cover",
                "path",
                "timestamp",
                "pubdate",
                "last_modified",
                "isbn",
                "lccn",
            ],
            parser=lambda x: BookMetadata(
                id=x[0],
                title=x[1],
                sort=x[2],
                author_sort=x[3],
                series_index=x[4],
                has_cover=x[5],
                path=x[6],
                timestamp=x[7],
                pubdate=x[8],
                last_modified=x[9],
                isbn=x[10],
                lccn=x[11],
            ),
        )

    def add_book_to_books_table(
        self,
        title: str,
        series_index: Optional[int] = None,
        author_sort: Optional[str] = None,
        isbn: Optional[str] = None,
        lccn: Optional[str] = None,
        path: Optional[str] = None,
        has_cover: Optional[str] = None,
    ):
        fields = ["title"]
        values = [title]

        if series_index is not None:
            fields.append("series_index")
            values.append(series_index)

        if author_sort is not None:
            fields.append("author_sort")
            values.append(author_sort)

        if isbn is not None:
            fields.append("isbn")
            values.append(isbn)

        if lccn is not None:
            fields.append("lccn")
            values.append(lccn)

        if path is not None:
            fields.append("path")
            values.append(path)

        if has_cover is not None:
            fields.append("has_cover")
            values.append(has_cover)

        self._insert_in_table(table_name=TableName.books, fields=fields, values=values)
