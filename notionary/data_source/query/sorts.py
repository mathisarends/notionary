from enum import StrEnum
from typing import Any

from pydantic import BaseModel, model_serializer


class SortDirection(StrEnum):
    ASCENDING = "ascending"
    DESCENDING = "descending"


class PropertySort(BaseModel):
    property: str
    direction: SortDirection = SortDirection.ASCENDING

    @model_serializer
    def _serialize(self) -> dict[str, Any]:
        return {
            "property": self.property,
            "direction": self.direction.value,
        }


class TimestampSort(BaseModel):
    timestamp: str
    direction: SortDirection = SortDirection.ASCENDING

    @model_serializer
    def _serialize(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "direction": self.direction.value,
        }


type QuerySort = PropertySort | TimestampSort
