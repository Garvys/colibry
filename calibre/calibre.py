from pathlib import Path

class CalibreLibrary:

    def __init__(self, library_path: Path) -> None:
        if not library_path.exists():
            raise ValueError(f"Library not found : {library_path}")
        self.library_path = library_path