from pydantic import BaseModel

from notionary.data_source.properties.schemas import AnyDataSourceProperty
from notionary.page.schemas import PageDto
from notionary.rich_text.schemas import RichText
from notionary.shared.object.dtos import NotionObjectResponseDto, NotionObjectUpdateDto
from notionary.shared.object.schemas import Parent


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
