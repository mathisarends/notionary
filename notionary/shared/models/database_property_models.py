from __future__ import annotations
from abc import ABC
from typing import Any, TypeVar, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator
from notionary.shared.models.shared_property_models import PropertyType


# ===== SHARED DATABASE SCHEMA MODELS =====


class DatabasePropertyOption(BaseModel):
    """Option for select/multi-select/status properties in database schema."""

    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    color: str
    description: str | None = None


class DatabaseStatusGroup(BaseModel):
    """Status group for status properties in database schema."""

    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    color: str
    option_ids: list[str]


class DatabaseStatusConfig(BaseModel):
    """Status configuration for status properties in database schema."""

    model_config = ConfigDict(extra="ignore")

    options: list[DatabasePropertyOption] = Field(default_factory=list)
    groups: list[DatabaseStatusGroup] = Field(default_factory=list)


class DatabaseSelectConfig(BaseModel):
    """Select configuration for select properties in database schema."""

    model_config = ConfigDict(extra="ignore")

    options: list[DatabasePropertyOption] = Field(default_factory=list)


class DatabaseMultiSelectConfig(BaseModel):
    """Multi-select configuration for multi-select properties in database schema."""

    model_config = ConfigDict(extra="ignore")

    options: list[DatabasePropertyOption] = Field(default_factory=list)


class DatabaseRelationConfig(BaseModel):
    """Relation configuration for relation properties in database schema."""

    model_config = ConfigDict(extra="ignore")

    database_id: str | None = None
    data_source_id: str | None = None
    type: str = "single_property"
    single_property: dict[str, Any] = Field(default_factory=dict)


class DatabaseDateConfig(BaseModel):
    """Date configuration for date properties in database schema."""

    model_config = ConfigDict(extra="ignore")

    # Date properties in schema are usually empty objects


class DatabaseTitleConfig(BaseModel):
    """Title configuration for title properties in database schema."""

    model_config = ConfigDict(extra="ignore")

    # Title properties in schema are usually empty objects


class DatabaseRichTextConfig(BaseModel):
    """Rich text configuration for rich text properties in database schema."""

    model_config = ConfigDict(extra="ignore")

    # Rich text properties in schema are usually empty objects


class DatabaseURLConfig(BaseModel):
    """URL configuration for URL properties in database schema."""

    model_config = ConfigDict(extra="ignore")

    # URL properties in schema are usually empty objects


class DatabasePeopleConfig(BaseModel):
    """People configuration for people properties in database schema."""

    model_config = ConfigDict(extra="ignore")

    # People properties in schema are usually empty objects


class DatabaseNumberConfig(BaseModel):
    """Number configuration for number properties in database schema."""

    model_config = ConfigDict(extra="ignore")

    format: str | None = None  # e.g., "number", "number_with_commas", "percent", etc.


class DatabaseCheckboxConfig(BaseModel):
    """Checkbox configuration for checkbox properties in database schema."""

    model_config = ConfigDict(extra="ignore")

    # Checkbox properties in schema are usually empty objects


class DatabaseEmailConfig(BaseModel):
    """Email configuration for email properties in database schema."""

    model_config = ConfigDict(extra="ignore")

    # Email properties in schema are usually empty objects


class DatabasePhoneNumberConfig(BaseModel):
    """Phone number configuration for phone number properties in database schema."""

    model_config = ConfigDict(extra="ignore")

    # Phone number properties in schema are usually empty objects


class DatabaseCreatedTimeConfig(BaseModel):
    """Created time configuration for created time properties in database schema."""

    model_config = ConfigDict(extra="ignore")

    # Created time properties in schema are usually empty objects


# ===== DATABASE SCHEMA PROPERTY MODELS =====


class DatabaseStatusProperty(BaseModel):
    """Status property for Database Schema responses."""

    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.STATUS
    status: DatabaseStatusConfig = Field(default_factory=DatabaseStatusConfig)

    @property
    def option_names(self) -> list[str]:
        """Get available status option names from database schema."""
        return [option.name for option in self.status.options]

    @property
    def group_names(self) -> list[str]:
        """Get available status group names from database schema."""
        return [group.name for group in self.status.groups]


class DatabaseMultiSelectProperty(BaseModel):
    """Multi-select property for Database Schema responses."""

    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.MULTI_SELECT
    multi_select: DatabaseMultiSelectConfig = Field(
        default_factory=DatabaseMultiSelectConfig
    )

    @property
    def option_names(self) -> list[str]:
        """Get available multi-select option names from database schema."""
        return [option.name for option in self.multi_select.options]


class DatabaseSelectProperty(BaseModel):
    """Select property for Database Schema responses."""

    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.SELECT
    select: DatabaseSelectConfig = Field(default_factory=DatabaseSelectConfig)

    @property
    def option_names(self) -> list[str]:
        """Get available select option names from database schema."""
        return [option.name for option in self.select.options]


class DatabaseRelationProperty(BaseModel):
    """Relation property for Database Schema responses."""

    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.RELATION
    relation: DatabaseRelationConfig = Field(default_factory=DatabaseRelationConfig)

    @property
    def related_database_id(self) -> str:
        """Get the related database ID."""
        return self.relation.database_id


class DatabaseDateProperty(BaseModel):
    """Date property for Database Schema responses."""

    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.DATE
    date: DatabaseDateConfig = Field(default_factory=DatabaseDateConfig)


class DatabaseTitleProperty(BaseModel):
    """Title property for Database Schema responses."""

    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.TITLE
    title: DatabaseTitleConfig = Field(default_factory=DatabaseTitleConfig)


class DatabaseRichTextProperty(BaseModel):
    """Rich text property for Database Schema responses."""

    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.RICH_TEXT
    rich_text: DatabaseRichTextConfig = Field(default_factory=DatabaseRichTextConfig)


class DatabaseURLProperty(BaseModel):
    """URL property for Database Schema responses."""

    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.URL
    url: DatabaseURLConfig = Field(default_factory=DatabaseURLConfig)


class DatabasePeopleProperty(BaseModel):
    """People property for Database Schema responses."""

    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.PEOPLE
    people: DatabasePeopleConfig = Field(default_factory=DatabasePeopleConfig)


class DatabaseNumberProperty(BaseModel):
    """Number property for Database Schema responses."""

    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.NUMBER
    number: DatabaseNumberConfig = Field(default_factory=DatabaseNumberConfig)

    @property
    def number_format(self) -> str | None:
        """Get the number format if specified."""
        return self.number.format


class DatabaseCheckboxProperty(BaseModel):
    """Checkbox property for Database Schema responses."""

    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.CHECKBOX
    checkbox: DatabaseCheckboxConfig = Field(default_factory=DatabaseCheckboxConfig)


class DatabaseEmailProperty(BaseModel):
    """Email property for Database Schema responses."""

    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.EMAIL
    email: DatabaseEmailConfig = Field(default_factory=DatabaseEmailConfig)


class DatabasePhoneNumberProperty(BaseModel):
    """Phone number property for Database Schema responses."""

    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.PHONE_NUMBER
    phone_number: DatabasePhoneNumberConfig = Field(
        default_factory=DatabasePhoneNumberConfig
    )


class DatabaseCreatedTimeProperty(BaseModel):
    """Created time property for Database Schema responses."""

    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.CREATED_TIME
    created_time: DatabaseCreatedTimeConfig = Field(
        default_factory=DatabaseCreatedTimeConfig
    )


# ===== TYPE UNION =====
DatabaseNotionProperty = Union[
    DatabaseStatusProperty,
    DatabaseMultiSelectProperty,
    DatabaseSelectProperty,
    DatabaseRelationProperty,
    DatabaseDateProperty,
    DatabaseTitleProperty,
    DatabaseRichTextProperty,
    DatabaseURLProperty,
    DatabasePeopleProperty,
    DatabaseNumberProperty,
    DatabaseCheckboxProperty,
    DatabaseEmailProperty,
    DatabasePhoneNumberProperty,
    DatabaseCreatedTimeProperty,
    dict[str, Any],  # Fallback
]

DatabasePropertyT = TypeVar("DatabasePropertyT", bound=DatabaseNotionProperty)


# ===== BASE CLASS =====
class NotionObjectWithDatabaseProperties(BaseModel, ABC):
    """
    Abstract base class for Notion objects that contain database schema properties.
    Provides automatic property parsing for Database DTOs (uses DatabaseNotionProperty models).
    """

    properties: dict[str, DatabaseNotionProperty] = Field(default_factory=dict)

    @field_validator("properties", mode="before")
    @classmethod
    def parse_database_properties(
        cls, v: dict[str, Any]
    ) -> dict[str, DatabaseNotionProperty]:
        """
        Parse database schema properties dictionary and create typed DatabaseNotionProperty objects.
        Falls back to dict[str, Any] for unknown property types.
        """
        if not v:
            return {}

        return {
            key: cls._create_database_property(prop_data)
            for key, prop_data in v.items()
        }

    @classmethod
    def _create_database_property(cls, prop_data: Any) -> DatabaseNotionProperty:
        if not isinstance(prop_data, dict) or "type" not in prop_data:
            return prop_data

        prop_type = prop_data.get("type")

        database_property_classes = {
            PropertyType.STATUS: DatabaseStatusProperty,
            PropertyType.MULTI_SELECT: DatabaseMultiSelectProperty,
            PropertyType.SELECT: DatabaseSelectProperty,
            PropertyType.RELATION: DatabaseRelationProperty,
            PropertyType.DATE: DatabaseDateProperty,
            PropertyType.TITLE: DatabaseTitleProperty,
            PropertyType.RICH_TEXT: DatabaseRichTextProperty,
            PropertyType.URL: DatabaseURLProperty,
            PropertyType.PEOPLE: DatabasePeopleProperty,
            PropertyType.NUMBER: DatabaseNumberProperty,
            PropertyType.CHECKBOX: DatabaseCheckboxProperty,
            PropertyType.EMAIL: DatabaseEmailProperty,
            PropertyType.PHONE_NUMBER: DatabasePhoneNumberProperty,
            PropertyType.CREATED_TIME: DatabaseCreatedTimeProperty,
        }

        property_class = database_property_classes.get(prop_type)

        if property_class:
            try:
                result = property_class(**prop_data)
                return result
            except Exception as e:
                print(f"❌ Database property error for {property_class.__name__}: {e}")
                return prop_data

        return prop_data
