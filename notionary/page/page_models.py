from __future__ import annotations
from typing import Any, Literal, Optional

from pydantic import BaseModel

from notionary.blocks.models import ParentObject
from notionary.shared.models.icon_models import Icon
from notionary.shared.models.cover_models import NotionCover

class NotionUser(BaseModel):
    object: str  # 'user'
    id: str

class NotionPageResponse(BaseModel):
    object: Literal["page"]
    id: str
    created_time: str
    last_edited_time: str
    created_by: NotionUser
    last_edited_by: NotionUser
    cover: Optional[NotionCover] = None
    icon: Optional[Icon] = None
    parent: ParentObject
    archived: bool
    in_trash: bool
    properties: dict[str, Any]
    url: str
    public_url: Optional[str] = None
