from __future__ import annotations

from enum import StrEnum
from typing import Any, Self

from pydantic import BaseModel, Field, field_validator


class SortDirection(StrEnum):
    ASCENDING = "ascending"
    DESCENDING = "descending"


class SortTimestamp(StrEnum):
    LAST_EDITED_TIME = "last_edited_time"
    CREATED_TIME = "created_time"


class ObjectType(StrEnum):
    PAGE = "page"
    DATA_SOURCE = "data_source"


class SearchConfig(BaseModel):
    query: str | None = None
    object_type: ObjectType | None = None
    sort_direction: SortDirection = SortDirection.DESCENDING
    sort_timestamp: SortTimestamp = SortTimestamp.LAST_EDITED_TIME
    page_size: int = Field(default=100, ge=1, le=100)  # Validierung: 1-100
    start_cursor: str | None = None

    @field_validator("query")
    @classmethod
    def replace_empty_query_with_none(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            return None
        return v

    def to_search_dict(self) -> dict[str, Any]:
        search_dict = {}

        if self.query:
            search_dict["query"] = self.query

        if self.object_type:
            search_dict["filter"] = {"property": "object", "value": self.object_type.value}

        search_dict["sort"] = {
            "direction": self.sort_direction.value,
            "timestamp": self.sort_timestamp.value,
        }

        search_dict["page_size"] = self.page_size

        if self.start_cursor:
            search_dict["start_cursor"] = self.start_cursor

        return search_dict


class SearchFilterBuilder:
    def __init__(self, config: SearchConfig = None) -> None:
        self.config = config or SearchConfig()

    def with_query(self, query: str) -> Self:
        self.config.query = query
        return self

    def with_pages_only(self) -> Self:
        self.config.object_type = ObjectType.PAGE
        return self

    def with_data_sources_only(self) -> Self:
        self.config.object_type = ObjectType.DATA_SOURCE
        return self

    def with_sort_direction(self, direction: SortDirection) -> Self:
        self.config.sort_direction = direction
        return self

    def with_sort_ascending(self) -> Self:
        return self.with_sort_direction(SortDirection.ASCENDING)

    def with_sort_descending(self) -> Self:
        return self.with_sort_direction(SortDirection.DESCENDING)

    def with_sort_timestamp(self, timestamp: SortTimestamp) -> Self:
        self.config.sort_timestamp = timestamp
        return self

    def with_sort_by_created_time(self) -> Self:
        return self.with_sort_timestamp(SortTimestamp.CREATED_TIME)

    def with_sort_by_last_edited(self) -> Self:
        return self.with_sort_timestamp(SortTimestamp.LAST_EDITED_TIME)

    def with_page_size(self, size: int) -> Self:
        self.config.page_size = min(size, 100)
        return self

    def with_start_cursor(self, cursor: str | None) -> Self:
        self.config.start_cursor = cursor
        return self

    def without_cursor(self) -> Self:
        self.config.start_cursor = None
        return self

    def build(self) -> dict[str, Any]:
        return self.config.to_search_dict()
