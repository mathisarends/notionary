from typing import Any, Literal

from pydantic import BaseModel, Field

from notionary.blocks.rich_text.rich_text_models import RichText
from notionary.page.page_models import NotionPageDto
from notionary.shared.entity.entity_models import EntityDto
from notionary.shared.models.cover_models import NotionCover
from notionary.shared.models.icon_models import Icon


class DataSourceDiscoveryDto(BaseModel):
    id: str
    name: str


class NotionDatabaseDto(EntityDto):
    title: list[RichText]
    description: list[RichText]
    is_inline: bool
    is_locked: bool
    data_sources: list[DataSourceDiscoveryDto] = Field(default_factory=list)
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


class NotionDatabaseUpdateDto(BaseModel):
    title: list[RichText] | None = None
    icon: Icon | None = None
    cover: NotionCover | None = None
    archived: bool | None = None
    description: list[RichText] | None = None
