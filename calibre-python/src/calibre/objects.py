from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from pathlib import Path

CalibreId = int


class BookMetadata(BaseModel):
    id: CalibreId
    model_config = ConfigDict(extra="allow")
    authors: str
    cover: Optional[Path] = None
    languages: Optional[List[str]] = None
    title: str
    formats: Optional[List[Path]] = None
    series: Optional[str] = None
    series_index: Optional[float] = None
