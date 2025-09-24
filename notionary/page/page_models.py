from __future__ import annotations

from typing import Literal

from notionary.page.properties.page_property_models import (
    NotionObjectWithProperties,
    PageProperty,
)
from notionary.shared.entities.entity_models import NotionEntityDto


class NotionPageDto(NotionEntityDto, NotionObjectWithProperties):
    object: Literal["page"]


class NotionPageUpdateDto(NotionObjectWithProperties):
    properties: dict[str, PageProperty] | None = None  # Überschreibt das Feld aus der Basisklasse
