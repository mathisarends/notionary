from enum import StrEnum
from typing import Protocol

from pydantic import BaseModel

from notionary.blocks.rich_text.models import RichText
from notionary.shared.models.cover import Cover
from notionary.shared.models.icon import Icon
from notionary.shared.models.parent import Parent
from notionary.user.schemas import PartialUserDto


class EntityWorkspaceQueryObjectType(StrEnum):
    PAGE = "page"
    DATA_SOURCE = "data_source"
    DATABASE = "database"


class EntityResponseDto(BaseModel):
    object: EntityWorkspaceQueryObjectType
    id: str
    created_time: str
    created_by: PartialUserDto
    last_edited_time: str
    last_edited_by: PartialUserDto
    cover: Cover | None = None
    icon: Icon | None = None
    parent: Parent
    in_trash: bool
    url: str
    public_url: str | None = None


class NotionEntityUpdateDto(BaseModel):
    icon: Icon | None = None
    cover: Cover | None = None
    in_trash: bool | None = None


class Titled(Protocol):
    title: list[RichText]


class Describable(Protocol):
    description: list[RichText] | None
