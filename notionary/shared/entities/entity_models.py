from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.shared.models.cover_models import NotionCover
from notionary.shared.models.icon_models import Icon
from notionary.shared.models.parent_models import NotionParent
from notionary.shared.models.user_models import NotionUser


class NotionEntityDto(BaseModel):
    id: str
    created_time: str
    last_edited_time: str
    created_by: NotionUser
    last_edited_by: NotionUser
    last_edited_by: NotionUser
    cover: NotionCover | None = None
    icon: Icon | None = None
    parent: NotionParent
    archived: bool
    in_trash: bool
    url: str
    public_url: str | None = None


class NotionDatabaseDto(NotionEntityDto):
    object: Literal["database"]
    title: list[RichTextObject]
    description: list[RichTextObject]
    is_inline: bool


class NotionPageDto(NotionEntityDto):
    object: Literal["page"]
