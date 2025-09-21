from __future__ import annotations

from abc import ABC
from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator

from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.shared.models.database_property_models import (
    PropertyType,
)
from notionary.shared.models.user_models import NotionUser


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


class PageStatusProperty(BaseModel):
    """Status property for Page responses."""

    model_config = ConfigDict(extra="ignore")

    id: str
    type: PropertyType = PropertyType.STATUS
    status: StatusOption | None = None
    options: list[StatusOption] = Field(default_factory=list)

    @property
    def option_names(self) -> list[str]:
        return [option.name for option in self.options]


class PageRelationProperty(BaseModel):
    """Relation property for Page responses."""

    model_config = ConfigDict(extra="ignore")

    id: str
    type: PropertyType = PropertyType.RELATION
    relation: list[RelationItem] = Field(default_factory=list)
    has_more: bool = False


class PageURLProperty(BaseModel):
    """URL property."""

    model_config = ConfigDict(extra="ignore")

    id: str
    type: PropertyType = PropertyType.URL
    url: str | None = None


class PageRichTextProperty(BaseModel):
    """Rich text property."""

    model_config = ConfigDict(extra="ignore")

    id: str
    type: PropertyType = PropertyType.RICH_TEXT
    rich_text: list[RichTextObject] = Field(default_factory=list)


class PageMultiSelectProperty(BaseModel):
    """Multi-select property for Page responses."""

    model_config = ConfigDict(extra="ignore")

    id: str
    type: PropertyType = PropertyType.MULTI_SELECT
    multi_select: list[SelectOption] = Field(default_factory=list)
    options: list[SelectOption] = Field(default_factory=list)

    @property
    def option_names(self) -> list[str]:
        """Get available multi-select option names from schema."""
        return [option.name for option in self.options]


class PageSelectProperty(BaseModel):
    """Select property for Page responses."""

    model_config = ConfigDict(extra="ignore")

    id: str
    type: PropertyType = PropertyType.SELECT
    select: SelectOption | None = None
    options: list[SelectOption] = Field(default_factory=list)

    @property
    def option_names(self) -> list[str]:
        return [option.name for option in self.options]


class PagePeopleProperty(BaseModel):
    """People property for Page responses."""

    model_config = ConfigDict(extra="ignore")

    id: str
    type: PropertyType = PropertyType.PEOPLE
    people: list[NotionUser] = Field(default_factory=list)


class PageDateProperty(BaseModel):
    """Date property."""

    model_config = ConfigDict(extra="ignore")

    id: str
    type: PropertyType = PropertyType.DATE
    date: DateValue | None = None


class PageTitleProperty(BaseModel):
    """Title property."""

    model_config = ConfigDict(extra="ignore")

    id: str
    type: PropertyType = PropertyType.TITLE
    title: list[RichTextObject] = Field(default_factory=list)


class PageNumberProperty(BaseModel):
    """Number property."""

    model_config = ConfigDict(extra="ignore")

    id: str
    type: PropertyType = PropertyType.NUMBER
    number: float | None = None


class PageCheckboxProperty(BaseModel):
    """Checkbox property."""

    model_config = ConfigDict(extra="ignore")

    id: str
    type: PropertyType = PropertyType.CHECKBOX
    checkbox: bool = False


class PageEmailProperty(BaseModel):
    """Email property."""

    model_config = ConfigDict(extra="ignore")

    id: str
    type: PropertyType = PropertyType.EMAIL
    email: str | None = None


class PagePhoneNumberProperty(BaseModel):
    """Phone number property."""

    model_config = ConfigDict(extra="ignore")

    id: str
    type: PropertyType = PropertyType.PHONE_NUMBER
    phone_number: str | None = None


class PageCreatedTimeProperty(BaseModel):
    """Created time property."""

    model_config = ConfigDict(extra="ignore")

    id: str
    type: PropertyType = PropertyType.CREATED_TIME
    created_time: str | None = None


# ===== TYPE UNIONS =====
PageProperty = (
    PageStatusProperty
    | PageRelationProperty
    | PageURLProperty
    | PageRichTextProperty
    | PageMultiSelectProperty
    | PageSelectProperty
    | PagePeopleProperty
    | PageDateProperty
    | PageTitleProperty
    | PageNumberProperty
    | PageCheckboxProperty
    | PageEmailProperty
    | PagePhoneNumberProperty
    | PageCreatedTimeProperty
    | dict[str, Any]  # Fallback
)

PagePropertyT = TypeVar("PagePropertyT", bound=PageProperty)


# ===== BASE CLASSES =====
class NotionObjectWithProperties(BaseModel, ABC):
    """
    Abstract base class for Notion objects that contain properties.
    Provides automatic property parsing for Page DTOs (uses PageProperty models).
    """

    properties: dict[str, PageProperty] = Field(default_factory=dict)

    @field_validator("properties", mode="before")
    @classmethod
    def parse_properties(cls, v: dict[str, Any]) -> dict[str, PageProperty]:
        """
        Parse the given properties dictionary and create typed PageProperty objects where possible.
        Falls back to dict[str, Any] for unknown property types.
        """
        if not v:
            return {}

        return {key: cls._create_property(prop_data) for key, prop_data in v.items()}

    @classmethod
    def _create_property(cls, prop_data: Any) -> PageProperty:
        if not isinstance(prop_data, dict) or "type" not in prop_data:
            return prop_data

        prop_type = prop_data.get("type")

        property_classes = {
            PropertyType.STATUS: PageStatusProperty,
            PropertyType.RELATION: PageRelationProperty,
            PropertyType.URL: PageURLProperty,
            PropertyType.RICH_TEXT: PageRichTextProperty,
            PropertyType.MULTI_SELECT: PageMultiSelectProperty,
            PropertyType.SELECT: PageSelectProperty,
            PropertyType.PEOPLE: PagePeopleProperty,
            PropertyType.DATE: PageDateProperty,
            PropertyType.TITLE: PageTitleProperty,
            PropertyType.NUMBER: PageNumberProperty,
            PropertyType.CHECKBOX: PageCheckboxProperty,
            PropertyType.EMAIL: PageEmailProperty,
            PropertyType.PHONE_NUMBER: PagePhoneNumberProperty,
            PropertyType.CREATED_TIME: PageCreatedTimeProperty,
        }

        property_class = property_classes.get(prop_type)

        if property_class:
            try:
                result = property_class(**prop_data)
                return result
            except Exception as e:
                print(f"❌ Exception creating {property_class.__name__}: {e}")
                print(f"❌ Property data that failed: {prop_data}")
                import traceback

                traceback.print_exc()
                return prop_data

        return prop_data
