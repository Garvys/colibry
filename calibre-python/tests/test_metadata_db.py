from calibre.metadata_db import (
    MetadataDB,
    AuthorMetadata,
    SerieMetadata,
    BookAuthorLinkMetadata,
    BookSerieLinkMetadata,
    BookMetadata,
    BookAggregatedMetadata,
    BookStructuredMetadata,
)
from datetime import datetime


def test_empty_metadata(tmp_path):
    db = MetadataDB.new_empty_db(tmp_path / "db")

    assert db.list_authors_from_authors_table() == []
    assert db.list_series_from_series_table() == []
    assert db.list_book_authors_links() == []
    assert db.list_book_series_link() == []
    assert db.lists_books_from_books_table() == []


def test_authors(tmp_path):
    db = MetadataDB.new_empty_db(tmp_path / "db")

    db.add_author_to_authors_table("David Bowie", "David Bowie")

    db.add_author_to_authors_table("queen", "queen")

    db.add_author_to_authors_table("David Bowie", "David Bowie")

    db.add_author_to_authors_table("david bowie", "david bowie")

    assert db.get_author_id("David Bowie") == 1
    assert db.get_author_id("david bowie") == 1
    assert db.get_author_id("queen") == 2
    assert db.get_author_id("lol") is None

    res = db.list_authors_from_authors_table()
    assert res == [
        AuthorMetadata(id=1, name="David Bowie", sort="David Bowie"),
        AuthorMetadata(id=2, name="queen", sort="queen"),
    ]

    res = db.list_authors_from_authors_table(author_id=2)
    assert res == [
        AuthorMetadata(id=2, name="queen", sort="queen"),
    ]

    db.update_author_in_authors_table(id=1, name="DD", sort="EE")

    res = db.list_authors_from_authors_table()
    assert res == [
        AuthorMetadata(id=1, name="DD", sort="EE"),
        AuthorMetadata(id=2, name="queen", sort="queen"),
    ]


def test_series(tmp_path):
    db = MetadataDB.new_empty_db(tmp_path / "db")

    db.add_serie_to_series_table("Silo", "Silo")

    db.add_serie_to_series_table("Game of Thrones", "Game of Thrones")

    db.add_serie_to_series_table("SILO", "SILO")

    db.add_serie_to_series_table("silo", "silo")

    assert db.get_serie_id("Silo") == 1
    assert db.get_serie_id("SILO") == 1
    assert db.get_serie_id("silo") == 1
    assert db.get_serie_id("Game of Thrones") == 2
    assert db.get_serie_id("lol") is None

    res = db.list_series_from_series_table()
    assert res == [
        SerieMetadata(id=1, name="Silo", sort="Silo"),
        SerieMetadata(id=2, name="Game of Thrones", sort="Game of Thrones"),
    ]

    res = db.list_series_from_series_table(serie_id=2)
    assert res == [
        SerieMetadata(id=2, name="Game of Thrones", sort="Game of Thrones"),
    ]


def test_books_authors_link(tmp_path):
    db = MetadataDB.new_empty_db(tmp_path / "db")

    # Can't insert a link if the book don't exist in the DB
    db.add_book_to_books_table(title="B2")  # book id 2
    db.add_book_to_books_table(title="B3")  # book id 3
    db.add_book_to_books_table(title="B4")  # book id 4

    # Can't insert a link if the author don't exist in the DB
    db.add_author_to_authors_table(name="S1", sort="S1")  # author 1
    db.add_author_to_authors_table(name="S2", sort="S2")  # author 2
    db.add_author_to_authors_table(name="S3", sort="S3")  # author 3
    db.add_author_to_authors_table(name="S4", sort="S4")  # author 4

    db.add_book_author_link(2, 3)
    db.add_book_author_link(3, 2)
    db.add_book_author_link(2, 3)
    db.add_book_author_link(4, 4)

    res = db.list_book_authors_links()
    assert res == [
        BookAuthorLinkMetadata(id=1, book_id=2, author_id=3),
        BookAuthorLinkMetadata(id=2, book_id=3, author_id=2),
        BookAuthorLinkMetadata(id=3, book_id=4, author_id=4),
    ]

    res = db.list_book_authors_links(book_id=3)
    assert res == [
        BookAuthorLinkMetadata(id=2, book_id=3, author_id=2),
    ]


def test_books_series_link(tmp_path):
    db = MetadataDB.new_empty_db(tmp_path / "db")

    # Can't insert a link if the book don't exist in the DB
    db.add_book_to_books_table(title="B2")  # book id 2
    db.add_book_to_books_table(title="B3")  # book id 3
    db.add_book_to_books_table(title="B4")  # book id 4

    # Can't insert a link if the series don't exist in the DB
    db.add_serie_to_series_table(name="S1", sort="S1")  # serie 1
    db.add_serie_to_series_table(name="S2", sort="S2")  # serie 2
    db.add_serie_to_series_table(name="S3", sort="S3")  # serie 3
    db.add_serie_to_series_table(name="S4", sort="S4")  # serie 4

    db.add_book_serie_link(2, 3)
    db.add_book_serie_link(3, 2)
    db.add_book_serie_link(2, 3)
    db.add_book_serie_link(4, 4)

    res = db.list_book_series_link()
    assert res == [
        BookSerieLinkMetadata(id=1, book_id=2, serie_id=3),
        BookSerieLinkMetadata(id=2, book_id=3, serie_id=2),
        BookSerieLinkMetadata(id=3, book_id=4, serie_id=4),
    ]

    res = db.list_book_series_link(book_id=2)
    assert res == [
        BookSerieLinkMetadata(id=1, book_id=2, serie_id=3),
    ]


def test_books(tmp_path):
    db = MetadataDB.new_empty_db(tmp_path / "db")

    assert db.lists_books_from_books_table() == []

    id_b1 = db.add_book_to_books_table(title="B1")
    id_b2 = db.add_book_to_books_table(
        title="B2",
        series_index=3,
        author_sort="pouet",
        isbn="isbn",
        lccn="lccn",
        path="mypath",
        has_cover=True,
    )

    assert id_b1 == 2
    assert id_b2 == 3

    now = datetime.now()

    res = db.lists_books_from_books_table()
    res = [
        r.model_copy(update={"timestamp": now, "pubdate": now, "last_modified": now})
        for r in res
    ]
    assert res == [
        BookMetadata(
            id=2,
            title="B1",
            sort="B1",
            series_index=1,
            author_sort=None,
            path="",
            has_cover=False,
            timestamp=now,
            pubdate=now,
            last_modified=now,
            isbn="",
            lccn="",
        ),
        BookMetadata(
            id=3,
            title="B2",
            sort="B2",
            series_index=3,
            author_sort="pouet",
            path="mypath",
            has_cover=True,
            timestamp=now,
            pubdate=now,
            last_modified=now,
            isbn="isbn",
            lccn="lccn",
        ),
    ]


def test_meta(tmp_path):
    db = MetadataDB.new_empty_db(tmp_path / "db")

    now = datetime.now()

    assert db.list_books_from_meta_table() == []

    db.add_book_to_books_table(title="Silo Origin")

    res = db.list_books_from_meta_table()
    res = [r.model_copy(update={"timestamp": now}) for r in res]

    assert res == [
        BookAggregatedMetadata(
            id=2,
            title="Silo Origin",
            authors=None,
            series=None,
            series_index=1,
            timestamp=now,
            author_sort=None,
            sort="Silo Origin",
            path="",
            lccn="",
            isbn="",
        )
    ]


def test_books_structured(tmp_path):
    db = MetadataDB.new_empty_db(tmp_path / "db")

    now = datetime.now()

    assert db.list_books_structured() == []

    db.add_book(title="Silo", authors=[("Hugh Howey", "hugh,howey")])
    db.add_book(title="Silo Origins", authors=[("Hugh Howey", "hugh,howey")])

    assert len(db.list_authors_from_authors_table()) == 1
    assert len(db.list_series_from_series_table()) == 0

    res = db.list_books_structured()
    res = [r.copy_and_override_datetimes(now) for r in res]

    assert res == [
        BookStructuredMetadata(
            book=BookMetadata(id=2, title="Silo", sort="Silo"),
            authors=[AuthorMetadata(id=1, name="Hugh Howey", sort="hugh,howey")],
            series=[],
        ).copy_and_override_datetimes(now),
        BookStructuredMetadata(
            book=BookMetadata(id=3, title="Silo Origins", sort="Silo Origins"),
            authors=[AuthorMetadata(id=1, name="Hugh Howey", sort="hugh,howey")],
            series=[],
        ).copy_and_override_datetimes(now)
    ]
