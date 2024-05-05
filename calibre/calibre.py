import subprocess
from pathlib import Path
from pydantic import BaseModel, ConfigDict, TypeAdapter
from typing import List, Optional
import json


class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


def run_shell(cmd):
    res = subprocess.run(cmd, stdout=subprocess.PIPE)
    if res.returncode != 0:
        raise ValueError(f"Error while running cmd {cmd}: {res.stdout}")
    return res.stdout


class CalibreMetadata(BaseModel):
    authors: str
    cover: str
    id: int
    languages: List[str]
    title: str
    formats: List[str]
    series: Optional[str] = None
    series_index: Optional[float] = None


def extract_catalog(library_path: Path) -> List[CalibreMetadata]:
    res = run_shell(
        [
            "calibredb",
            "--library-path",
            str(library_path),
            "list",
            "--fields",
            "cover,authors,title,languages,series,series_index,formats",
            "--for-machine",
        ]
    )
    res = res.strip().decode("utf-8")
    res = json.loads(res)

    m = TypeAdapter(List[CalibreMetadata]).validate_python(res)

    return m


if __name__ == "__main__":
    extract_catalog("/home/garvys/Documents/calibre-dashboard/library")
