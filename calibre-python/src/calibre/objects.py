from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from pathlib import Path

LibraryId = int


class BookMetadata(BaseModel):
    id: LibraryId
    model_config = ConfigDict(extra="allow")
    authors: str
    cover: Optional[Path] = None
    languages: Optional[List[str]] = None
    title: Optional[str] = None
    formats: Optional[List[Path]] = None
    series: Optional[str] = None
    series_index: Optional[float] = None
