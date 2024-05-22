from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from pathlib import Path
from datetime import datetime
from enum import Enum


class CalibreField(str, Enum):
    # id = 'id' # book ID
    authors = "authors"
    title = "title"
    cover = "cover"
    formats = "formats"
    series = "series"
    series_index = "series_index"
    timestamp = "timestamp"


class BookMetadata(BaseModel):
    id: int
    authors: Optional[str] = None
    cover: Optional[Path] = None
    languages: Optional[List[str]] = None
    title: Optional[str] = None
    formats: Optional[List[Path]] = None
    series: Optional[str] = None
    series_index: Optional[float] = None
    timestamp: Optional[datetime] = None

    model_config = ConfigDict(extra="allow")
