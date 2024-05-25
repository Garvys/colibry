from pydantic import BaseModel
from calibre.objects import CalibreField
from typing import List
from calibre.filters.filter import Filter


class SearchParams(BaseModel):
    fields: List[CalibreField] = []
    filters: List[Filter] = []
