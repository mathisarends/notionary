from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_serializer


class SortDirection(StrEnum):
    ASCENDING = "ascending"
    DESCENDING = "descending"


class SortTimestamp(StrEnum):
    LAST_EDITED_TIME = "last_edited_time"
    CREATED_TIME = "created_time"


class WorkspaceQueryObjectType(StrEnum):
    PAGE = "page"
    DATA_SOURCE = "data_source"


class WorkspaceQueryConfig(BaseModel):
    query: str | None = None
    object_type: WorkspaceQueryObjectType | None = None
    sort_direction: SortDirection = SortDirection.DESCENDING
    sort_timestamp: SortTimestamp = SortTimestamp.LAST_EDITED_TIME
    page_size: int = Field(default=100, ge=1, le=100)
    start_cursor: str | None = None

    @field_validator("query")
    @classmethod
    def replace_empty_query_with_none(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            return None
        return value

    @model_serializer
    def serialize_model(self) -> dict[str, Any]:
        search_dict: dict[str, Any] = {}

        if self.query:
            search_dict["query"] = self.query

        if self.object_type:
            search_dict["filter"] = {
                "property": "object",
                "value": self.object_type.value,
            }

        search_dict["sort"] = {
            "direction": self.sort_direction.value,
            "timestamp": self.sort_timestamp.value,
        }

        search_dict["page_size"] = self.page_size

        if self.start_cursor:
            search_dict["start_cursor"] = self.start_cursor

        return search_dict
