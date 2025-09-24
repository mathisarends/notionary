from __future__ import annotations

from notionary.page.properties.page_property_models import (
    NotionObjectWithProperties,
    PageProperty,
)
from notionary.shared.entities.entity_models import NotionEntityResponseDto


class NotionPageDto(NotionEntityResponseDto, NotionObjectWithProperties): ...


class NotionPageUpdateDto(NotionObjectWithProperties):
    properties: dict[str, PageProperty] | None = None  # Überschreibt das Feld aus der Basisklasse
