from typing import Any, Literal

from pydantic import BaseModel, Field

from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.page.page_models import NotionPageDto
from notionary.shared.models.cover_models import NotionCover
from notionary.shared.models.icon_models import Icon
from notionary.shared.models.parent_models import NotionParent


class DataSourceDiscoveryDto(BaseModel):
    id: str
    name: str


class NotionDatabaseDto(BaseModel):
    object: Literal["database"] = "database"
    id: str
    title: list[RichTextObject]
    description: list[RichTextObject]
    parent: NotionParent
    is_inline: bool
    in_trash: bool
    is_locked: bool
    created_time: str
    last_edited_time: str
    data_sources: list[DataSourceDiscoveryDto] = Field(default_factory=list)
    icon: Icon | None = None
    cover: NotionCover | None = None
    url: str
    public_url: str | None = None


class NotionQueryDatabaseResponse(BaseModel):
    object: Literal["list"]
    results: list[NotionPageDto]
    next_cursor: str | None = None
    has_more: bool
    type: Literal["page_or_data_source"]
    page_or_data_source: dict[str, Any]
    request_id: str


class NotionDatabaseSearchResponse(BaseModel):
    object: Literal["list"]
    results: list[NotionDatabaseDto]
    next_cursor: str | None = None
    has_more: bool
    type: Literal["page_or_data_source"]
    page_or_data_source: dict[str, Any]
    request_id: str


class NotionDatabaseUpdateDto(BaseModel):
    title: list[RichTextObject] | None = None
    icon: Icon | None = None
    cover: NotionCover | None = None
    archived: bool | None = None
    description: list[RichTextObject] | None = None
