from pathlib import Path
import shutil
import sqlite3

class MetadataDB:

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)

    @classmethod
    def new_empty_db(cls, new_db_path: Path):
        path_empty_library = Path(__file__).resolve().parent / "empty_library"
        path_empty_db = path_empty_library / "metadata.db"
        shutil.copy(path_empty_db, new_db_path)
        return cls(new_db_path)
    
    def list_authors(self):
        cursor = self.connection.cursor()
        res = cursor.execute("SELECT * FROM authors")
        res = res.fetchall()
        return res

