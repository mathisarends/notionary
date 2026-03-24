from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_serializer

from notionary.shared.entity.schemas import EntityResponseDto
from notionary.shared.models.file import File
from notionary.shared.models.icon import Icon
from notionary.shared.rich_text.schemas import RichText


class _DataSourceDiscoveryDto(BaseModel):
    id: str
    name: str


class DatabaseDto(EntityResponseDto):
    title: list[RichText]
    description: list[RichText]
    is_inline: bool
    is_locked: bool
    data_sources: list[_DataSourceDiscoveryDto] = Field(default_factory=list)
    url: str
    public_url: str | None = None


class DatabaseUpdateDto(BaseModel):
    title: list[RichText] | None = None
    icon: Icon | None = None
    cover: File | None = None
    archived: bool | None = None
    description: list[RichText] | None = None


class SortDirection(StrEnum):
    ASCENDING = "ascending"
    DESCENDING = "descending"


class SortTimestamp(StrEnum):
    LAST_EDITED_TIME = "last_edited_time"
    CREATED_TIME = "created_time"


class DatabaseQueryConfig(BaseModel):
    query: str | None = None
    sort_direction: SortDirection = SortDirection.DESCENDING
    sort_timestamp: SortTimestamp = SortTimestamp.LAST_EDITED_TIME
    page_size: int = Field(default=100, ge=1, le=100)
    total_results_limit: int | None = None

    @field_validator("query")
    @classmethod
    def replace_empty_query_with_none(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            return None
        return value

    @model_serializer
    def to_api_params(self) -> dict[str, Any]:
        params: dict[str, Any] = {
            "filter": {"property": "object", "value": "database"},
            "sort": {
                "direction": self.sort_direction.value,
                "timestamp": self.sort_timestamp.value,
            },
            "page_size": self.page_size,
        }
        if self.query:
            params["query"] = self.query
        return params
