from enum import StrEnum

from pydantic import BaseModel

from notionary.shared.models.cover_models import NotionCover
from notionary.shared.models.icon_models import Icon
from notionary.shared.models.parent_models import NotionParent


class EntityObjectType(StrEnum):
    PAGE = "page"
    DATA_SOURCE = "data_source"
    DATABASE = "database"


class EntityDto(BaseModel):
    object: EntityObjectType
    id: str
    created_time: str
    last_edited_time: str
    cover: NotionCover | None = None
    icon: Icon | None = None
    parent: NotionParent
    in_trash: bool
    url: str
    public_url: str | None = None


class NotionEntityUpdateDto(BaseModel):
    icon: Icon | None = None
    cover: NotionCover | None = None
    in_trash: bool | None = None
