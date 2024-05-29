import pytest
from pathlib import Path
from typing import List
from calibre import CalibreDB, CalibreSql

@pytest.mark.parametrize("library_class", [CalibreDB, CalibreSql])
def test_clone(library_class, tmp_path: Path, ebook_paths: List[Path]):
    library1 = library_class.new_empty_library(tmp_path / "library1")

    library2 = library1.clone(tmp_path / "library2").add(ebook_paths)

    assert len(library1.list_books()) == 0
    assert len(library2.list_books()) == len(ebook_paths)
