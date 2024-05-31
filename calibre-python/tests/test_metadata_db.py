from calibre.metadata_db import (
    MetadataDB,
    AuthorMetadata,
    SerieMetadata,
    BookAuthorLinkMetadata,
    BookSerieLinkMetadata,
    BookMetadata,
)


def test_empty_metadata(tmp_path):
    db = MetadataDB.new_empty_db(tmp_path / "db")

    assert db.list_authors_from_authors_table() == []
    assert db.list_series_from_series_table() == []
    assert db.list_book_authors_link() == []
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

    res = db.list_book_authors_link()
    assert res == [
        BookAuthorLinkMetadata(id=1, book_id=2, author_id=3),
        BookAuthorLinkMetadata(id=2, book_id=3, author_id=2),
        BookAuthorLinkMetadata(id=3, book_id=4, author_id=4),
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


def test_books(tmp_path):
    db = MetadataDB.new_empty_db(tmp_path / "db")

    assert db.lists_books_from_books_table() == []

    db.add_book_to_books_table(title="B1")
    db.add_book_to_books_table(title="B2")

    res = db.lists_books_from_books_table()
    assert res == [
        BookMetadata(id=2, title="B1", sort="B1", series_index=1, author_sort=None),
        BookMetadata(id=3, title="B2", sort="B2", series_index=1, author_sort=None),
    ]
