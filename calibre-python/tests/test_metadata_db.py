from calibre.metadata_db import MetadataDB, AuthorMetadata, SerieMetadata


def test_empty_metadata(tmp_path):
    db = MetadataDB.new_empty_db(tmp_path / "db")

    assert db.list_authors_from_authors_table() == []
    assert db.list_series_from_series_table() == []


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
