from calibre.library import Library
from pathlib import Path
from typing import List


def test_new_add_list(tmp_path: Path, ebook_paths: List[Path]):
    lib = Library.new_empty_library(tmp_path / "library")

    lib.add(ebooks=ebook_paths)

    res = lib.list()

    assert len(res) == len(ebook_paths)