from pathlib import Path
import shutil
import sqlite3
from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Optional, List, Callable, Any, Dict, Tuple
from calibre.sql_aggregators import title_sort, SortedConcatenate, Concatenate
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
    sort: str = ""
    author_sort: Optional[str] = None
    series_index: int = 1
    path: str = ""
    has_cover: bool = False
    timestamp: datetime = Field(default_factory=datetime.now)
    pubdate: datetime = Field(default_factory=datetime.now)
    last_modified: datetime = Field(default_factory=datetime.now)
    isbn: str = ""
    lccn: str = ""

    def copy_and_override_datetimes(self, dt_override: datetime) -> "BookMetadata":
        return self.model_copy(
            update={
                "timestamp": dt_override,
                "pubdate": dt_override,
                "last_modified": dt_override,
            }
        )


class BookAuthorLinkMetadata(StrictBaseModel):
    id: int
    book_id: int
    author_id: int


class BookSerieLinkMetadata(StrictBaseModel):
    id: int
    book_id: int
    serie_id: int


class DataMetadata(StrictBaseModel):
    id: int
    book_id: int
    format: str
    uncompressed_size: int
    name: str


class BookAggregatedMetadata(StrictBaseModel):
    id: int
    title: str
    authors: Optional[str]
    timestamp: datetime
    pubdate: datetime
    series: Optional[str]
    series_index: int
    sort: str
    author_sort: Optional[str]
    isbn: str
    path: str
    lccn: str


class BookStructuredMetadata(StrictBaseModel):
    book: BookMetadata
    authors: List[AuthorMetadata]
    serie: Optional[SerieMetadata]

    def copy_and_override_datetimes(self, dt_override: datetime) -> "BookMetadata":
        book_overriden = self.book.copy_and_override_datetimes(dt_override)
        return self.model_copy(update={"book": book_overriden})


class TableName(str, Enum):
    authors = "authors"
    series = "series"
    books = "books"
    books_authors_link = "books_authors_link"
    books_series_link = "books_series_link"
    meta = "meta"
    data = "data"


class MetadataDB:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)
        self.connection.create_function("title_sort", 1, title_sort)
        self.connection.create_function("uuid4", 0, lambda: str(uuid.uuid4()))
        self.connection.create_aggregate("sortconcat", 2, SortedConcatenate)
        self.connection.create_aggregate("concat", 1, Concatenate)

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
        # Filter to apply, should map key to value
        filter: Optional[Dict[str, str]] = None,
        limit: Optional[int] = None,
    ) -> List[BaseModel]:
        cursor = self.connection.cursor()

        query = f"SELECT {', '.join(fields)} FROM {str(table_name.value)}"

        if filter:
            q = " AND ".join([f"{key} = '{value}'" for key, value in filter.items()])
            if q:
                query += " WHERE " + q

        if limit is not None:
            query += f" LIMIT {limit}"

        res = cursor.execute(query)
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
        return cursor.lastrowid

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

    def list_authors_from_authors_table(
        self, author_id: Optional[int] = None
    ) -> List[AuthorMetadata]:
        filter = None
        if author_id is not None:
            filter = {}
            filter["id"] = author_id

        return self._list_table(
            TableName.authors,
            ["id", "name", "sort"],
            lambda x: AuthorMetadata(id=x[0], name=x[1], sort=x[2]),
            filter=filter,
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

    def list_series_from_series_table(
        self, serie_id: Optional[int] = None
    ) -> List[SerieMetadata]:
        filter = {}
        if serie_id is not None:
            filter["id"] = serie_id

        return self._list_table(
            TableName.series,
            ["id", "name", "sort"],
            lambda x: SerieMetadata(id=x[0], name=x[1], sort=x[2]),
            filter=filter,
        )

    def add_serie_to_series_table(self, name: str, sort: str):
        self._insert_in_table(
            table_name=TableName.series, fields=["name", "sort"], values=[name, sort]
        )

    def get_serie_id(self, name: str) -> Optional[int]:
        return self._get_id_from_field(
            table_name=TableName.series, field_name="name", value=name
        )

    def list_book_authors_links(
        self, book_id: Optional[int] = None
    ) -> List[BookAuthorLinkMetadata]:
        filter = None
        if book_id is not None:
            filter = {}
            filter["book"] = book_id

        return self._list_table(
            table_name=TableName.books_authors_link,
            fields=["id", "book", "author"],
            parser=lambda x: BookAuthorLinkMetadata(
                id=x[0], book_id=x[1], author_id=x[2]
            ),
            filter=filter,
        )

    def add_book_author_link(self, book_id: int, author_id: int):
        self._insert_in_table(
            table_name=TableName.books_authors_link,
            fields=["book", "author"],
            values=[book_id, author_id],
        )

    def list_book_series_link(
        self, book_id: Optional[int] = None, limit: Optional[int] = None
    ) -> List[BookSerieLinkMetadata]:
        filter = {}
        if book_id is not None:
            filter["book"] = book_id

        return self._list_table(
            table_name=TableName.books_series_link,
            fields=["id", "book", "series"],
            parser=lambda x: BookSerieLinkMetadata(
                id=x[0], book_id=x[1], serie_id=x[2]
            ),
            filter=filter,
            limit=limit,
        )

    def add_book_serie_link(self, book_id: int, serie_id: int):
        self._insert_in_table(
            table_name=TableName.books_series_link,
            fields=["book", "series"],
            values=[book_id, serie_id],
        )

    def list_data_table(self, book_id: Optional[int] = None) -> List[DataMetadata]:
        filter = {}
        if book_id is not None:
            filter["book"] = book_id
        return self._list_table(
            table_name=TableName.data,
            fields=["id", "book", "format", "uncompressed_size", "name"],
            parser=lambda x: DataMetadata(
                id=x[0], book_id=x[1], format=x[2], uncompressed_size=x[3], name=x[4]
            ),
            filter=filter,
        )

    def add_to_data_table(
        self, book_id: int, format: str, uncompressed_size: int, name: str
    ):
        self._insert_in_table(
            table_name=TableName.data,
            fields=["book", "format", "uncompressed_size", "name"],
            values=[book_id, format, uncompressed_size, name],
        )

    def lists_books_from_books_table(self) -> List[BookMetadata]:
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

    # Returns the BOOK ID of the inserted book
    def add_book_to_books_table(
        self,
        title: str,
        series_index: Optional[int] = None,
        author_sort: Optional[str] = None,
        isbn: Optional[str] = None,
        lccn: Optional[str] = None,
        path: Optional[str] = None,
        has_cover: Optional[str] = None,
    ) -> int:
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

        last_row_id = self._insert_in_table(
            table_name=TableName.books, fields=fields, values=values
        )
        return last_row_id

    def list_books_from_meta_table(self) -> List[BookAggregatedMetadata]:
        return self._list_table(
            table_name=TableName.meta,
            fields=[
                "id",
                "title",
                "authors",
                "timestamp",
                "series",
                "series_index",
                "sort",
                "author_sort",
                "path",
                "isbn",
                "lccn",
                "pubdate",
            ],
            parser=lambda x: BookAggregatedMetadata(
                id=x[0],
                title=x[1],
                authors=x[2],
                timestamp=x[3],
                series=x[4],
                series_index=x[5],
                sort=x[6],
                author_sort=x[7],
                path=x[8],
                isbn=x[9],
                lccn=x[10],
                pubdate=x[11],
            ),
        )

    def list_books_structured(self) -> List[BookStructuredMetadata]:
        book_metadatas = self.lists_books_from_books_table()

        # TODO: We could probably reduce a bit the number of SQL calls by doing some JOINT
        res = []
        for book_metadata in book_metadatas:
            # Need to find all the authors attached to that book
            book_author_links = self.list_book_authors_links(book_id=book_metadata.id)

            authors = [
                self.list_authors_from_authors_table(
                    author_id=book_author_link.author_id
                )[0]
                for book_author_link in book_author_links
            ]

            # Need to find all the series attached to that book
            book_series_links = self.list_book_series_link(
                book_id=book_metadata.id, limit=1
            )

            serie = None
            if book_series_links:
                serie = self.list_series_from_series_table(
                    serie_id=book_series_links[0].serie_id
                )[0]

            res.append(
                BookStructuredMetadata(book=book_metadata, authors=authors, serie=serie)
            )

        return res

    def add_book(
        self,
        title: str,
        authors: Optional[List[Tuple[str, str]]] = None,
        series_index: Optional[int] = None,
        author_sort: Optional[str] = None,
        isbn: Optional[str] = None,
        lccn: Optional[str] = None,
        path: Optional[str] = None,
        has_cover: Optional[str] = None,
        serie: Optional[Tuple[str, str]] = None,
    ) -> int:
        book_id = self.add_book_to_books_table(
            title=title,
            series_index=series_index,
            author_sort=author_sort,
            isbn=isbn,
            lccn=lccn,
            path=path,
            has_cover=has_cover,
        )

        if authors:
            for name, sort in authors:
                # Insert author if not already present in DB
                self.add_author_to_authors_table(name=name, sort=sort)

                # Retrieve ID
                author_id = self.get_author_id(name)
                if author_id is None:
                    raise ValueError(
                        f"None author_id whereas the author has been inserted : {name}"
                    )

                # Add book author link
                self.add_book_author_link(book_id=book_id, author_id=author_id)

        if serie is not None:
            name, sort = serie
            # Insert serie if not already present in DB
            self.add_serie_to_series_table(name=name, sort=sort)

            # Retrieve ID
            serie_id = self.get_serie_id(name)
            if serie_id is None:
                raise ValueError(
                    f"None serie_id whereas the serie has been inserted : {name}"
                )

            # Add book serie link
            self.add_book_serie_link(book_id=book_id, serie_id=serie_id)

        return book_id
