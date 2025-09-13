from __future__ import annotations
from typing import Any, Literal

from pydantic import BaseModel

from notionary.blocks.models import ParentObject
from notionary.shared.models.icon_models import Icon
from notionary.shared.models.cover_models import NotionCover


class NotionUser(BaseModel):
    object: str  # 'user'
    id: str


class NotionPageDto(BaseModel):
    object: Literal["page"]
    id: str
    created_time: str
    last_edited_time: str
    created_by: NotionUser
    last_edited_by: NotionUser
    cover: NotionCover | None = None
    icon: Icon | None = None
    parent: ParentObject
    archived: bool
    in_trash: bool
    properties: dict[str, Any]
    url: str
    public_url: str | None = None


class NotionPageUpdateDto(BaseModel):
    cover: NotionCover | None = None
    icon: Icon | None = None
    properties: dict[str, Any] | None = None
    archived: bool | None = None

    @classmethod
    def from_notion_page_dto(cls, page: NotionPageDto) -> NotionPageUpdateDto:
        return cls(
            cover=page.cover,
            icon=page.icon,
            properties=page.properties,
            archived=page.archived,
        )
