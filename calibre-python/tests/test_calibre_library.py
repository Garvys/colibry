from calibre.calibre import CalibreLibrary
from pathlib import Path
from typing import List


def test_lol(tmp_path: Path, ebook_paths: List[Path]):
    CalibreLibrary.new_empty_library(tmp_path / "library")