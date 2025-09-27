from pydantic import BaseModel

from notionary.shared.models.cover_models import NotionCover
from notionary.shared.models.icon_models import Icon


class NotionEntityUpdateDto(BaseModel):
    icon: Icon | None = None
    cover: NotionCover | None = None
    archived: bool | None = None
