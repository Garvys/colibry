from __future__ import annotations
from pathlib import Path
import subprocess
from typing import List, Optional
import json
from calibre.objects import BookMetadata, LibraryId
from pydantic import TypeAdapter
import epub


def run_shell(cmd):
    res = subprocess.run(cmd, stdout=subprocess.PIPE)
    if res.returncode != 0:
        raise ValueError(f"Error while running cmd {cmd}: {res.stdout}")
    return res.stdout


class CalibreLibrary:
    def __init__(self, library_path: Path):
        if not library_path.exists():
            raise ValueError(f"Library not found : {library_path}")
        self.library_path = library_path

    def _run_calibredb(self, l: List[str]):
        return run_shell(["calibredb", "--with-library", str(self.library_path), *l])

    @classmethod
    def new_empty_library(cls, new_library_path: Path) -> CalibreLibrary:
        path_empty_library = Path(__file__).resolve().parent / "empty_library"

        run_shell(
            [
                "calibredb",
                "--with-library",
                str(path_empty_library),
                "clone",
                str(new_library_path),
            ]
        )

        return cls(library_path=new_library_path)

    def clone(self, new_library_path: Path) -> CalibreLibrary:
        self._run_calibredb(["clone", str(new_library_path)])

        return CalibreLibrary(library_path=new_library_path)

    def add(self, ebooks: List[Path]):
        self._run_calibredb(["add", *[str(p) for p in ebooks]])

        return self

    def list(
        self,
        limit: Optional[int] = None,
        sort_by: Optional[str] = None,
        ascending: bool = False,
        search: str = "",
    ) -> List[BookMetadata]:
        cmd = ["list", "--for-machine", "--fields", "authors,title,cover,formats,series,series_index,timestamp"]
        if limit is not None:
            cmd += ["--limit", str(limit)]
        if sort_by is not None:
            cmd += ["--sort-by", sort_by]
        if ascending:
            cmd += ["--ascending"]
        if search:
            cmd += ["--search", search]
        res = self._run_calibredb(cmd)
        return TypeAdapter(List[BookMetadata]).validate_python(
            json.loads(res.decode("utf-8"))
        )

    def list_authors(self) -> List[str]:
        res = self._run_calibredb(["list", "--for-machine", "--fields", "authors"])
        books_metadata = TypeAdapter(List[BookMetadata]).validate_python(
            json.loads(res.decode("utf-8"))
        )
        return [e.authors for e in books_metadata if e.authors]

    def remove_from_ids(self, ids: List[LibraryId]) -> CalibreLibrary:
        self._run_calibredb(["remove", ",".join([str(e) for e in ids])])

        return self

    def remove_books(self, books: List[BookMetadata]):
        return self.remove_from_ids(ids=[e.id for e in books])

    def show_metadata(self, library_id: LibraryId) -> BookMetadata:
        res = self._run_calibredb(["show_metadata", str(library_id), "--as-opf"])

        raise NotImplementedError

        # print(res)

        # print(epub.opf.parse_opf(res.decode("utf-8")).metadata.titles)
