from calibre.objects import InternalCalibreField
from typing import Any, Union
from pydantic import BaseModel
from abc import abstractmethod


class Filter(BaseModel):
    @abstractmethod
    def to_calibredb_filter(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def to_sql_filter(self) -> str:
        raise NotImplementedError


class EqualityFilter(Filter):
    field: InternalCalibreField
    value: Any

    def to_calibredb_filter(self) -> str:
        return f'{self.field.value}:"{str(self.value)}"'

    def to_sql_filter(self) -> str:
        return f'{self.field.value}="{str(self.value)}"'

    @classmethod
    def with_id(cls, id: Union[int, str]):
        return cls(field=InternalCalibreField.id, value=id)
