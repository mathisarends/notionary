from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel

from notionary.shared.entity.entity_models import NotionEntityDto


class NotionUserDto(BaseModel):
    object: Literal["user"] = "user"
    id: str


# TODO: Hierfragen ob man eine so spezifische DTO braucht oder ob NotionEntityDto reicht
class NotionPageOrDataSourceDto(NotionEntityDto):
    created_by: NotionUserDto
    last_edited_by: NotionUserDto
    archived: bool
    properties: dict[str, Any]
