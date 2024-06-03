from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any
from pathlib import Path
from datetime import datetime
from enum import Enum


class ExternalBookMetadata(BaseModel):
    id: int
    title: str
    authors: str
    author_sort: Optional[str]
    series: Optional[str] = None
    series_index: int
    isbn: str
    pubdate: datetime
    timestamp: datetime
    cover: Optional[Path]
    formats: List[Path]
    last_modified: datetime
    size: int

    model_config = ConfigDict(extra="forbid")

    def model_copy_and_remove_microseconds(self) -> "ExternalBookMetadata":
        timestamp = self.timestamp.replace(microsecond=0)
        last_modified = self.last_modified.replace(microsecond=0)
        return self.model_copy(
            update={"timestamp": timestamp, "last_modified": last_modified}
        )
