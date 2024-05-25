from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from pathlib import Path
from datetime import datetime
from enum import Enum


class CalibreField(str, Enum):
    authors = "authors"
    cover = "cover"
    formats = "formats"
    series = "series"
    series_index = "series_index"
    timestamp = "timestamp"


class BookMetadata(BaseModel):
    id: int
    title: str
    authors: Optional[str] = None
    cover: Optional[Path] = None
    languages: Optional[List[str]] = None
    formats: Optional[List[Path]] = None
    series: Optional[str] = None
    series_index: Optional[float] = None
    timestamp: Optional[datetime] = None

    model_config = ConfigDict(extra="allow")


class InternalCalibreField(str, Enum):
    id = "id"
    title = "title"
    path = "path"
    authors = "authors"
    formats = "formats"
    series = "series"
    series_index = "series_index"


class InternalBookMetadata(BaseModel):
    id: int
    title: str
    path: Optional[Path] = None
    authors: Optional[str] = None
    formats: Optional[str] = None
    series: Optional[str] = None
    series_index: Optional[float] = None
    timestamp: Optional[datetime] = None
