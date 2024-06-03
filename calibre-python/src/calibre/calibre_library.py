from __future__ import annotations

import shutil
from abc import abstractmethod
from pathlib import Path
from typing import List

from calibre.objects import ExternalBookMetadata


class AbstractCalibreLibrary:
    def __init__(self, library_path: Path) -> None:
        if not library_path.exists():
            raise ValueError(f"Library not found : {library_path}")
        self.library_path = library_path

    @classmethod
    def new_empty_library(cls, new_library_path: Path) -> AbstractCalibreLibrary:
        path_empty_library = Path(__file__).resolve().parent / "empty_library"

        shutil.copytree(path_empty_library, new_library_path)

        return cls(library_path=new_library_path)

    def clone(self, new_library_path: Path) -> AbstractCalibreLibrary:
        shutil.copytree(self.library_path, new_library_path)
        return self.__class__(new_library_path)

    @abstractmethod
    def list_books(self) -> List[ExternalBookMetadata]:
        raise NotImplementedError

    @abstractmethod
    def add_books(self, ebook: List[Path]):
        raise NotImplementedError
