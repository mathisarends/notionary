from __future__ import annotations
from abc import ABC
from enum import StrEnum
from typing import Any, TypeVar, Union

from pydantic import BaseModel, Field, field_validator

from notionary.blocks.rich_text.rich_text_models import RichTextObject


# Use these typings to make notion types cleaner
class PropertyType(StrEnum):
    """Enum for property types used in NotionPage."""

    SELECT = "select"
    MULTI_SELECT = "multi_select"
    STATUS = "status"
    RELATION = "relation"
    TITLE = "title"
    RICH_TEXT = "rich_text"
    NUMBER = "number"
    DATE = "date"
    CHECKBOX = "checkbox"
    URL = "url"
    EMAIL = "email"


class SelectOption(BaseModel):
    """Represents a select option."""

    id: str
    name: str


class StatusOption(BaseModel):
    """Represents a status option."""

    id: str
    name: str


class RelationItem(BaseModel):
    """Represents a relation item."""

    id: str


class DateValue(BaseModel):
    """Represents a date value."""

    start: str
    end: str | None = None
    time_zone: str | None = None


# Property Models
class StatusProperty(BaseModel):
    """Status property."""

    id: str
    type: PropertyType = PropertyType.STATUS
    status: StatusOption | None = None


class RelationProperty(BaseModel):
    """Relation property."""

    id: str
    type: PropertyType = PropertyType.RELATION
    relation: list[RelationItem] = Field(default_factory=list)
    has_more: bool = False


class URLProperty(BaseModel):
    """URL property."""

    id: str
    type: PropertyType = PropertyType.URL
    url: str | None = None


class RichTextProperty(BaseModel):
    """Rich text property."""

    id: str
    type: PropertyType = PropertyType.RICH_TEXT
    rich_text: list[RichTextObject] = Field(default_factory=list)


class MultiSelectProperty(BaseModel):
    """Multi-select property."""

    id: str
    type: PropertyType = PropertyType.MULTI_SELECT
    multi_select: list[SelectOption] = Field(default_factory=list)


class DateProperty(BaseModel):
    """Date property."""

    id: str
    type: PropertyType = PropertyType.DATE
    date: DateValue | None = None


class TitleProperty(BaseModel):
    """Title property."""

    id: str
    type: PropertyType = PropertyType.TITLE
    title: list[RichTextObject] = Field(default_factory=list)


class NumberProperty(BaseModel):
    """Number property."""

    id: str
    type: PropertyType = PropertyType.NUMBER
    number: float | None = None


class CheckboxProperty(BaseModel):
    """Checkbox property."""

    id: str
    type: PropertyType = PropertyType.CHECKBOX
    checkbox: bool = False


class EmailProperty(BaseModel):
    """Email property."""

    id: str
    type: PropertyType = PropertyType.EMAIL
    email: str | None = None


NotionProperty = Union[
    StatusProperty,
    RelationProperty,
    URLProperty,
    RichTextProperty,
    MultiSelectProperty,
    DateProperty,
    TitleProperty,
    NumberProperty,
    CheckboxProperty,
    EmailProperty,
    dict[str, Any],  # Fallback
]

PropertyT = TypeVar('PropertyT', bound=NotionProperty)

class NotionObjectWithProperties(BaseModel, ABC):
    """
    Abstract base class for Notion objects that contain properties.
    Provides automatic property parsing for both Page and Database DTOs.
    """

    properties: dict[str, NotionProperty] = Field(default_factory=dict)

    @field_validator("properties", mode="before")
    @classmethod
    def parse_properties(cls, v: dict[str, Any]) -> dict[str, NotionProperty]:
        """
        Parse the given properties dictionary and create typed NotionProperty objects where possible.
        Falls back to dict[str, Any] for unknown property types.
        """
        if not v:
            return {}

        return {key: cls._create_property(prop_data) for key, prop_data in v.items()}

    @classmethod
    def _create_property(cls, prop_data: Any) -> NotionProperty:
        if not isinstance(prop_data, dict) or "type" not in prop_data:
            return prop_data

        prop_type = prop_data.get("type")

        property_classes = {
            PropertyType.STATUS: StatusProperty,
            PropertyType.RELATION: RelationProperty,
            PropertyType.URL: URLProperty,
            PropertyType.RICH_TEXT: RichTextProperty,
            PropertyType.MULTI_SELECT: MultiSelectProperty,
            PropertyType.DATE: DateProperty,
            PropertyType.TITLE: TitleProperty,
            PropertyType.NUMBER: NumberProperty,
            PropertyType.CHECKBOX: CheckboxProperty,
            PropertyType.EMAIL: EmailProperty,
        }

        property_class = property_classes.get(prop_type)

        if property_class:
            try:
                return property_class(**prop_data)
            except Exception:
                return prop_data

        return prop_data
