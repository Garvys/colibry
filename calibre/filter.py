from calibre.extract import CalibreLibraryMetadata
from calibre.pydantic_utils import StrictBaseModel
from typing import List, Optional


class SearchFilters(StrictBaseModel):
    text: Optional[str]


def filter_library_metadata(
    library: List[CalibreLibraryMetadata], filters: SearchFilters
) -> List[CalibreLibraryMetadata]:
    res = []

    for entry in library:
        if filters.text:
            normalized_text = entry.authors + entry.title
            if entry.series:
                normalized_text += entry.series

            if filters.text.lower() not in normalized_text.lower():
                continue

        res.append(entry)

    return res
