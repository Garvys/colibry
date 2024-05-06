from pytest import fixture
from pathlib import Path
from typing import List

@fixture(scope="session")
def data_folder() -> Path:
    return Path(__file__).resolve().parents[2] / "data"


@fixture(scope="session")
def ebook_paths(data_folder: Path) -> List[Path]:
    ebooks_dir = data_folder / "ebooks"
    return list(ebooks_dir.glob("*.epub"))