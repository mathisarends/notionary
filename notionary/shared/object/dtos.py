from __future__ import annotations

from typing import TYPE_CHECKING, Literal
from uuid import UUID

from pydantic import BaseModel

if TYPE_CHECKING:
    from notionary.shared.object.icon.schemas import AnyIcon
    from notionary.shared.object.schemas import File, Parent
    from notionary.user.schemas import PartialUserDto


class NotionObjectResponseDto(BaseModel):
    object: Literal["page", "database", "data_source"]
    id: UUID
    created_time: str
    created_by: PartialUserDto
    last_edited_time: str
    last_edited_by: PartialUserDto
    cover: File | None = None
    icon: AnyIcon | None = None
    parent: Parent
    in_trash: bool
    url: str


class NotionObjectUpdateDto(BaseModel):
    icon: AnyIcon | None = None
    cover: File | None = None
    in_trash: bool | None = None
