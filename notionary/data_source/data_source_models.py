from typing import Literal

from pydantic import BaseModel

from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.data_source.properties.data_source_properties_mixin import DataSourcePropertiesMixin
from notionary.page.page_models import NotionPageDto
from notionary.shared.entity.entity_models import EntityDto, NotionEntityUpdateDto
from notionary.shared.entity.user_context_mixin import UserContextMixin
from notionary.shared.models.parent_models import NotionParent


class DataSourceDto(EntityDto, UserContextMixin, DataSourcePropertiesMixin):
    database_parent: NotionParent
    title: list[RichTextObject]
    description: list[RichTextObject]
    archived: bool


class UpdateDataSourceDto(NotionEntityUpdateDto):
    title: list[RichTextObject]
    description: list[RichTextObject]
    archived: bool


class DataSourceSearchResponse(BaseModel):
    results: list[DataSourceDto]
    next_cursor: str | None = None
    has_more: bool
    type: Literal["page_or_data_source"]


class QueryDataSourceResponse(BaseModel):
    object: Literal["list"]
    results: list[NotionPageDto]
    next_cursor: str | None = None
    has_more: bool
