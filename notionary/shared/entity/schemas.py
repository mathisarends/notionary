from typing import Literal

from pydantic import BaseModel

from notionary.shared.models.file import File
from notionary.shared.models.icon import Icon
from notionary.shared.models.parent import Parent
from notionary.user.schemas import PartialUserDto


class EntityResponseDto(BaseModel):
    object: Literal["page", "database", "data_source"]
    id: str
    created_time: str
    created_by: PartialUserDto
    last_edited_time: str
    last_edited_by: PartialUserDto
    cover: File | None = None
    icon: Icon | None = None
    parent: Parent
    in_trash: bool
    url: str


class NotionEntityUpdateDto(BaseModel):
    icon: Icon | None = None
    cover: File | None = None
    in_trash: bool | None = None
