from calibre.metadata_db import MetadataDB, AuthorMetadata

def test_empty_metadata(tmp_path):
    db = MetadataDB.new_empty_db(tmp_path / "db")

    authors = db.list_authors()
    
    assert authors == []

def test_authors(tmp_path):
    db = MetadataDB.new_empty_db(tmp_path / "db")

    db.add_author("David Bowie")
    db.add_author("queen")
    db.add_author("David Bowie")
    db.add_author("david bowie")

    res = db.list_authors()
    assert res == [
        AuthorMetadata(id=1, name="David Bowie", sort="David Bowie"),
        AuthorMetadata(id=2, name="queen", sort="queen")
    ]