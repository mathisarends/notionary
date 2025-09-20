from __future__ import annotations
from typing import Literal


from notionary.shared.models.icon_models import Icon
from notionary.shared.models.cover_models import NotionCover
from notionary.shared.models.parent_models import NotionParent
from notionary.page.properties.page_property_models import (
    NotionObjectWithProperties,
    PageProperty,
)
from notionary.shared.models.user_models import NotionUser


class NotionPageDto(NotionObjectWithProperties):
    object: Literal["page"]
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


class NotionPageUpdateDto(NotionObjectWithProperties):
    cover: NotionCover | None = None
    icon: Icon | None = None
    archived: bool | None = None
    properties: dict[str, PageProperty] | None = (
        None  # Überschreibt das Feld aus der Basisklasse
    )

    @classmethod
    def from_notion_page_dto(cls, page: NotionPageDto) -> NotionPageUpdateDto:
        return cls(
            cover=page.cover,
            icon=page.icon,
            properties=page.properties,
            archived=page.archived,
        )
