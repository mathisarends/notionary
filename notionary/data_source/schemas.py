from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from notionary.data_source.properties.schemas import AnyDataSourceProperty
from notionary.data_source.query.filters import QueryFilter
from notionary.data_source.query.sorts import QuerySort
from notionary.page.schemas import PageDto
from notionary.rich_text import RichText
from notionary.shared.object.dtos import NotionObjectResponseDto, NotionObjectUpdateDto
from notionary.shared.object.schemas import Parent


class QueryResultType(StrEnum):
    PAGE = "page"


class QueryDataSourceRequest(BaseModel):
    filter: QueryFilter | None = None
    sorts: list[QuerySort] | None = None
    start_cursor: str | None = None
    page_size: int | None = Field(default=None, ge=1, le=100)
    filter_properties: list[str] | None = None
    in_trash: bool | None = None
    result_type: QueryResultType = QueryResultType.PAGE

    def to_api_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if self.filter is not None:
            payload["filter"] = self.filter.model_dump(
                mode="json", exclude_none=True, by_alias=True
            )
        if self.sorts is not None:
            payload["sorts"] = [s.model_dump(mode="json") for s in self.sorts]
        if self.start_cursor is not None:
            payload["start_cursor"] = self.start_cursor
        if self.page_size is not None:
            payload["page_size"] = self.page_size
        if self.in_trash is not None:
            payload["in_trash"] = self.in_trash
        return payload

    def to_query_params(self) -> dict[str, list[str]]:
        params: dict[str, list[str]] = {}
        if self.filter_properties:
            params["filter_properties"] = self.filter_properties
        return params


class UpdateDataSourceDto(NotionObjectUpdateDto):
    title: list[RichText] | None = None


class CreateDataSourceRequest(BaseModel):
    parent: dict
    properties: dict
    title: list[RichText] | None = None


class QueryDataSourceResponse(BaseModel):
    results: list[PageDto]
    next_cursor: str | None = None
    has_more: bool


class DataSourceDto(NotionObjectResponseDto):
    database_parent: Parent
    title: list[RichText]
    description: list[RichText]
    properties: dict[str, AnyDataSourceProperty]


class DataSourceTemplate(BaseModel):
    id: str
    name: str
    is_default: bool


class ListTemplatesResponse(BaseModel):
    templates: list[DataSourceTemplate]
    has_more: bool
    next_cursor: str | None = None
