from __future__ import annotations
from pathlib import Path
import subprocess
from typing import List
import json
from calibre.objects import BookMetadata
from pydantic import TypeAdapter


def run_shell(cmd):
    res = subprocess.run(cmd, stdout=subprocess.PIPE)
    if res.returncode != 0:
        raise ValueError(f"Error while running cmd {cmd}: {res.stdout}")
    return res.stdout


class Library:

    def __init__(self, library_path: Path):
        if not library_path.exists():
            raise ValueError(f"Library not found : {library_path}")
        self.library_path = library_path

    def _run_calibredb(self, l: List[str]):
        return run_shell([
            "calibredb",
            "--with-library",
            str(self.library_path),
            *l
        ])

    @classmethod
    def new_empty_library(cls, new_library_path: Path) -> Library:
        path_empty_library = Path(__file__).resolve().parent / "empty_library"

        run_shell([
            "calibredb",
            "--with-library",
            str(path_empty_library),
            "clone",
            str(new_library_path)
        ])

        return cls(library_path=new_library_path)

    
    def clone(self, new_library_path: Path) -> Library:
        self._run_calibredb([
            "clone", str(new_library_path)
        ])

        return Library(library_path=new_library_path)
    
    def add(self, ebooks: List[Path]):
        self._run_calibredb([
            "add", *[str(p) for p in ebooks]
        ])

        return self
    
    def list(self) -> List[BookMetadata]:
        res = self._run_calibredb(
            ["list", "--for-machine", "--fields", "all"]
        )
        return TypeAdapter(List[BookMetadata]).validate_python(json.loads(res.decode("utf-8")))

    


