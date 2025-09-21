from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel

from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.page.page_models import NotionPageDto
from notionary.shared.models.cover_models import NotionCover
from notionary.shared.models.database_property_models import (
    NotionObjectWithDatabaseProperties,
)
from notionary.shared.models.icon_models import Icon
from notionary.shared.models.parent_models import NotionParent
from notionary.shared.models.user_models import NotionUser


class NoionDatabaseDto(NotionObjectWithDatabaseProperties):
    """
    Represents the response from the Notion API when retrieving a database.
    """

    object: Literal["database"]
    id: str
    cover: Any | None = None
    icon: Icon | None = None
    cover: NotionCover | None = None
    created_time: str
    last_edited_time: str
    created_by: NotionUser
    last_edited_by: NotionUser
    title: list[RichTextObject]
    description: list[Any]
    is_inline: bool
    parent: NotionParent
    url: str
    public_url: str | None = None
    archived: bool
    in_trash: bool


class NotionQueryDatabaseResponse(BaseModel):
    """
    Notion database query response model for querying pages within a database.
    """

    object: Literal["list"]
    results: list[NotionPageDto]
    next_cursor: str | None = None
    has_more: bool
    type: Literal["page_or_database"]
    page_or_database: dict[str, Any]
    request_id: str


class NotionDatabaseSearchResponse(BaseModel):
    """
    Notion search response model for database-only searches.
    """

    object: Literal["list"]
    results: list[NoionDatabaseDto]
    next_cursor: str | None = None
    has_more: bool
    type: Literal["page_or_database"]
    page_or_database: dict[str, Any]
    request_id: str
