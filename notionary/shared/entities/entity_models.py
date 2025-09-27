from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel

from notionary.shared.models.cover_models import NotionCover
from notionary.shared.models.icon_models import Icon
from notionary.shared.models.parent_models import NotionParent


class NotionUserDto(BaseModel):
    object: Literal["user"] = "user"
    id: str


# TODO: Rename to PageOrDataSourceResponseDto
class NotionEntityResponseDto(BaseModel):
    object: Literal["page", "data_source"]
    id: str
    created_time: str
    last_edited_time: str
    created_by: NotionUserDto
    last_edited_by: NotionUserDto
    cover: NotionCover | None = None
    icon: Icon | None = None
    parent: NotionParent
    archived: bool
    in_trash: bool
    properties: dict[str, Any]


class NotionEntityUpdateDto(BaseModel):
    icon: Icon | None = None
    cover: NotionCover | None = None
    archived: bool | None = None
