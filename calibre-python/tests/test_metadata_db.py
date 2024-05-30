from calibre.metadata_db import MetadataDB, AuthorMetadata, SerieMetadata

def test_empty_metadata(tmp_path):
    db = MetadataDB.new_empty_db(tmp_path / "db")

    assert db.list_authors() == []
    assert db.list_series() == []

def test_authors(tmp_path):
    db = MetadataDB.new_empty_db(tmp_path / "db")

    id_bowie = db.add_author("David Bowie", "David Bowie")
    assert id_bowie == 1

    id_queen = db.add_author("queen", "queen")
    assert id_queen == 2

    id_bowie = db.add_author("David Bowie", "David Bowie")
    assert id_bowie == 1

    id_bowie = db.add_author("david bowie", "david bowie")
    assert id_bowie == 1

    assert db.get_author_id("David Bowie") == 1
    assert db.get_author_id("queen") == 2
    assert db.get_author_id("lol") is None


    res = db.list_authors()
    assert res == [
        AuthorMetadata(id=1, name="David Bowie", sort="David Bowie"),
        AuthorMetadata(id=2, name="queen", sort="queen")
    ]

def test_series(tmp_path):
    db = MetadataDB.new_empty_db(tmp_path / "db")

    id_silo = db.add_serie("Silo", "Silo")
    assert id_silo == 1

    id_got = db.add_serie("Game of Thrones", "Game of Thrones")
    assert id_got == 2

    id_silo = db.add_serie("SILO", "SILO")
    assert id_silo == 1

    id_silo = db.add_serie("silo", "silo")
    assert id_silo == 1

    assert db.get_serie_id("Silo") == 1
    assert db.get_serie_id("Game of Thrones") == 2
    assert db.get_serie_id("lol") is None


    res = db.list_series()
    assert res == [
        SerieMetadata(id=1, name="Silo", sort="Silo"),
        SerieMetadata(id=2, name="Game of Thrones", sort="Game of Thrones")
    ]