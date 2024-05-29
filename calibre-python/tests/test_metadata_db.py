from calibre.metadata_db import MetadataDB

def test_empty_metadata(tmp_path):
    db = MetadataDB.new_empty_db(tmp_path / "db")

    authors = db.list_authors()
    
    assert authors == []