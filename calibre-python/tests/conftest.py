from pytest import fixture
from pathlib import Path
from typing import List
from calibre import CalibreDB, CalibreSql


@fixture(scope="session")
def data_folder() -> Path:
    return Path(__file__).resolve().parents[2] / "data"


@fixture(scope="session")
def ebook_paths(data_folder: Path) -> List[Path]:
    ebooks_dir = data_folder / "ebooks"
    return list(ebooks_dir.glob("*.epub"))


@fixture(scope="session")
def library_calibredb(ebook_paths: List[Path]):
    from tempfile import TemporaryDirectory

    tmp = TemporaryDirectory()

    db = CalibreDB.new_empty_library(Path(tmp.name) / "library").add_books(
        ebooks=ebook_paths
    )
    # Attach tmp so that it gets removed when the db is destroyed
    db.tmp = tmp
    return db


@fixture(scope="session")
def library_calibresql(library_calibredb):
    return CalibreSql(library_path=library_calibredb.library_path)
