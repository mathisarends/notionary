from pydantic import BaseModel

from notionary.data_source.properties.schemas import AnyDataSourceProperty
from notionary.page.schemas import PageDto
from notionary.shared.entity.schemas import EntityResponseDto, NotionEntityUpdateDto
from notionary.shared.models.parent import Parent
from notionary.shared.rich_text.schemas import RichText


class UpdateDataSourceDto(NotionEntityUpdateDto):
    title: list[RichText]
    description: list[RichText]
    archived: bool


class QueryDataSourceResponse(BaseModel):
    results: list[PageDto]
    next_cursor: str | None = None
    has_more: bool


class DataSourceDto(EntityResponseDto):
    database_parent: Parent
    title: list[RichText]
    description: list[RichText]
    archived: bool
    properties: dict[str, AnyDataSourceProperty]
