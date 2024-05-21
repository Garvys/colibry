from __future__ import annotations

import shutil
from abc import abstractmethod
from pathlib import Path
from typing import List, Optional

from calibre.objects import BookMetadata


class CalibreLibrary:
    def __init__(self, library_path: Path) -> None:
        if not library_path.exists():
            raise ValueError(f"Library not found : {library_path}")
        self.library_path = library_path

    @classmethod
    def new_empty_library(cls, new_library_path: Path) -> CalibreLibrary:
        path_empty_library = Path(__file__).resolve().parent / "empty_library"

        shutil.copytree(path_empty_library, new_library_path)

        return cls(library_path=new_library_path)

    @abstractmethod
    def list(
        self,
        limit: Optional[int] = None,
        sort_by: Optional[str] = None,
        ascending: bool = False,
        search: str = "",
    ) -> List[BookMetadata]:
        raise NotImplementedError
