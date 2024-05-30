from pathlib import Path
import shutil
import sqlite3
from pydantic import BaseModel
from typing import Optional

class AuthorMetadata(BaseModel):
    id: int
    name: str
    sort: str


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
        res = cursor.execute("SELECT id, name, sort FROM authors")
        res = res.fetchall()
        res_parsed = []
        for e in res:
            res_parsed.append(AuthorMetadata(id=e[0], name=e[1], sort=e[2]))
        return res_parsed
    
    def add_author(self, name: str, sort: str) -> int:
        cursor = self.connection.cursor()
        cursor.execute(f"INSERT OR IGNORE INTO authors (name, sort) VALUES ('{name}', '{sort}')")

    def get_author_id(self, name: str) -> Optional[int]:
        cursor = self.connection.cursor()
        res = cursor.execute(f"SELECT id FROM authors where name = '{name}'")
        author_id = res.fetchone()
        return author_id[0] if author_id is not None else None

