from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel

from notionary.shared.models.cover_models import NotionCover
from notionary.shared.models.icon_models import Icon
from notionary.shared.models.parent_models import NotionParent
from notionary.shared.models.user_models import NotionUser


class EntityObjectType(StrEnum):
    PAGE = "page"
    DATABASE = "database"


class NotionEntityResponseDto(BaseModel):
    object: EntityObjectType
    id: str
    created_time: str
    last_edited_time: str
    created_by: NotionUser
    last_edited_by: NotionUser
    cover: NotionCover | None = None
    icon: Icon | None = None
    parent: NotionParent
    archived: bool
    in_trash: bool
    url: str
    public_url: str | None = None
    properties: dict[str, Any]
