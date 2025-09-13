from __future__ import annotations
from typing import Any, Literal, Optional

from pydantic import BaseModel
from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.page.page_models import NotionPageDto
from notionary.shared.models.cover_models import NotionCover
from notionary.shared.models.icon_models import Icon
from notionary.shared.models.parent_models import NotionParent
from notionary.shared.models.user_models import NotionUser


class NotionDatabaseResponse(BaseModel):
    """
    Represents the response from the Notion API when retrieving a database.
    """

    object: Literal["database"]
    id: str
    cover: Optional[Any] = None
    icon: Optional[Icon] = None
    cover: Optional[NotionCover] = None
    created_time: str
    last_edited_time: str
    created_by: NotionUser
    last_edited_by: NotionUser
    title: list[RichTextObject]
    description: list[Any]
    is_inline: bool
    properties: dict[
        str, Any
    ]  # Using Any for flexibility with different property schemas
    parent: NotionParent
    url: str
    public_url: Optional[str] = None
    archived: bool
    in_trash: bool


class NotionQueryDatabaseResponse(BaseModel):
    """
    Notion database query response model for querying pages within a database.
    """

    object: Literal["list"]
    results: list[NotionPageDto]
    next_cursor: Optional[str] = None
    has_more: bool
    type: Literal["page_or_database"]
    page_or_database: dict[str, Any]
    request_id: str


class NotionDatabaseSearchResponse(BaseModel):
    """
    Notion search response model for database-only searches.
    """

    object: Literal["list"]
    results: list[NotionDatabaseResponse]
    next_cursor: Optional[str] = None
    has_more: bool
    type: Literal["page_or_database"]
    page_or_database: dict[str, Any]
    request_id: str
