from typing import Any, Literal

from pydantic import BaseModel

from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.database.properties.database_properties_mixin import DatabasePropertiesMixin
from notionary.page.page_models import NotionPageDto
from notionary.shared.entities.entity_models import NotionEntityResponseDto
from notionary.shared.models.cover_models import NotionCover
from notionary.shared.models.icon_models import Icon


class NotionDatabaseDto(NotionEntityResponseDto, DatabasePropertiesMixin):
    title: list[RichTextObject]
    description: list[RichTextObject]
    is_inline: bool


class NotionQueryDatabaseResponse(BaseModel):
    object: Literal["list"]
    results: list[NotionPageDto]
    next_cursor: str | None = None
    has_more: bool
    type: Literal["page_or_database"]
    page_or_database: dict[str, Any]
    request_id: str


class NotionDatabaseSearchResponse(BaseModel):
    object: Literal["list"]
    results: list[NotionDatabaseDto]
    next_cursor: str | None = None
    has_more: bool
    type: Literal["page_or_database"]
    page_or_database: dict[str, Any]
    request_id: str


class NotionDatabaseUpdateDto(BaseModel):
    title: list[RichTextObject] | None = None
    icon: Icon | None = None
    cover: NotionCover | None = None
    archived: bool | None = None
    description: list[RichTextObject] | None = None
