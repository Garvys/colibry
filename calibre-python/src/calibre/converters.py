from calibre.objects import (
    CalibreField,
    InternalCalibreField,
    InternalBookMetadata,
    BookMetadata,
)
from pathlib import Path
from typing import List
from datetime import timezone


def calibre_field_external_to_internals(
    field: CalibreField,
) -> List[InternalCalibreField]:
    if field == CalibreField.authors:
        return [InternalCalibreField.authors]
    elif field == CalibreField.cover:
        return [InternalCalibreField.path]
    elif field == CalibreField.formats:
        return [InternalCalibreField.path, InternalCalibreField.formats]
    elif field == CalibreField.series:
        return [InternalCalibreField.series]
    elif field == CalibreField.series_index:
        return [InternalCalibreField.series_index]
    elif field == CalibreField.timestamp:
        return [CalibreField.timestamp]
    else:
        raise ValueError(f"Field not supported : {field}")


def book_metadata_internal_to_external(
    internal: InternalBookMetadata, library_path: Path, fields: List[CalibreField]
) -> BookMetadata:
    authors = None
    if CalibreField.authors in fields:
        authors = internal.authors

    cover = None
    if internal.path is not None and CalibreField.cover in fields:
        p = library_path / internal.path / "cover.jpg"
        if p.exists():
            cover = p

    timestamp = None
    if CalibreField.timestamp in fields:
        if internal.timestamp is not None:
            # Remove microsecond to be aligned with calibredb
            timestamp = internal.timestamp.replace(microsecond=0, tzinfo=timezone.utc)

    series_index = None
    if CalibreField.series_index in fields:
        series_index = internal.series_index

    series = None
    if CalibreField.series in fields:
        series = internal.series

    formats = None
    if CalibreField.formats in fields:
        if internal.path is None:
            raise ValueError("Path should be selected when searching for formats")
        folder_path = library_path / internal.path
        formats = []
        for format in internal.formats.split(","):
            for p in folder_path.glob(f"*.{format.lower()}"):
                formats.append(p)

    return BookMetadata(
        id=internal.id,
        title=internal.title,
        authors=authors,
        cover=cover,
        timestamp=timestamp,
        series_index=series_index,
        series=series,
        formats=formats,
    )
