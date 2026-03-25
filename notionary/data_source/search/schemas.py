from typing import Any

from pydantic import BaseModel, Field, field_validator, model_serializer

from notionary.shared.sorting import SortDirection, SortTimestamp


class DataSourceQueryConfig(BaseModel):
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
            "filter": {"property": "object", "value": "data_source"},
            "sort": {
                "direction": self.sort_direction.value,
                "timestamp": self.sort_timestamp.value,
            },
            "page_size": self.page_size,
        }
        if self.query:
            params["query"] = self.query
        return params
