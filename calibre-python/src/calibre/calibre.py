from __future__ import annotations
from pathlib import Path
import subprocess


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

    @classmethod
    def new_empty_library(cls, new_library_path: Path) -> CalibreLibrary:
        path_empty_library = Path(__file__).resolve().parent / "empty_library"

        run_shell([
            "calibredb",
            "--with-library",
            str(path_empty_library),
            "clone",
            str(new_library_path)
        ])

        return cls(library_path=new_library_path)

    
    def clone(self, new_library_path: Path) -> CalibreLibrary:
        run_shell([
            "calibredb",
            "--with-library",
            str(self.library_path),
            "clone",
            str(new_library_path)
        ])

        return CalibreLibrary(library_path=new_library_path)
    


