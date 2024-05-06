from calibre.extract import CalibreLibraryMetadata
from calibre.pydantic_utils import StrictBaseModel
from typing import List, Optional
from pydantic import BaseModel


class SearchFilters(StrictBaseModel):
    text: Optional[str]


def filter_library_metadata(
    library: List[CalibreLibraryMetadata], filters: SearchFilters
) -> List[CalibreLibraryMetadata]:
    res = []

    for entry in library:
        if filters.text:
            if not (
                filters.text.lower()
                in entry.authors.lower() + entry.title.lower() + entry.series.lower()
            ):
                continue

        res.append(entry)

    return res
