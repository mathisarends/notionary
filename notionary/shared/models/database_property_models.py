from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator

from notionary.shared.models.shared_property_models import PropertyType

# ===== SHARED DATABASE SCHEMA MODELS =====


class DatabasePropertyOption(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    color: str
    description: str | None = None


class DatabaseStatusGroup(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    color: str
    option_ids: list[str]


# This class has no mapping to the api but is a convenient wrapper to display options of status props
@dataclass
class EnrichedDatabaseStatusOption(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    color: str
    description: str | None = None
    group_name: str | None = None


class DatabaseStatusConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")

    options: list[DatabasePropertyOption] = Field(default_factory=list)
    groups: list[DatabaseStatusGroup] = Field(default_factory=list)

    @property
    def detailed_options(self) -> list[EnrichedDatabaseStatusOption]:
        option_to_group = {option_id: group.name for group in self.groups for option_id in group.option_ids}

        return [
            EnrichedDatabaseStatusOption(
                id=option.id,
                name=option.name,
                color=option.color,
                description=option.description,
                group_name=option_to_group.get(option.id),
            )
            for option in self.options
        ]


class DatabaseSelectConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    options: list[DatabasePropertyOption] = Field(default_factory=list)


class DatabaseMultiSelectConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    options: list[DatabasePropertyOption] = Field(default_factory=list)


class DatabaseRelationConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")

    database_id: str | None = None
    data_source_id: str | None = None
    type: str = "single_property"
    single_property: dict[str, Any] = Field(default_factory=dict)


class DatabaseDateConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")

    # Date properties in schema are usually empty objects


class DatabaseTitleConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")

    # Title properties in schema are usually empty objects


class DatabaseRichTextConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")

    # Rich text properties in schema are usually empty objects


class DatabaseURLConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")

    # URL properties in schema are usually empty objects


class DatabasePeopleConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")

    # People properties in schema are usually empty objects


class DatabaseNumberConfig(BaseModel):
    format: str | None = None  # e.g., "number", "number_with_commas", "percent", etc.


class DatabaseCheckboxConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")

    # Checkbox properties in schema are usually empty objects


class DatabaseEmailConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")

    # Email properties in schema are usually empty objects


class DatabasePhoneNumberConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")

    # Phone number properties in schema are usually empty objects


class DatabaseCreatedTimeConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")

    # Created time properties in schema are usually empty objects


# ===== DATABASE SCHEMA PROPERTY MODELS =====


class DatabaseStatusProperty(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.STATUS
    status: DatabaseStatusConfig = Field(default_factory=DatabaseStatusConfig)

    @property
    def option_names(self) -> list[str]:
        return [option.name for option in self.status.options]

    @property
    def group_names(self) -> list[str]:
        return [group.name for group in self.status.groups]


class DatabaseMultiSelectProperty(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.MULTI_SELECT
    multi_select: DatabaseMultiSelectConfig = Field(default_factory=DatabaseMultiSelectConfig)

    @property
    def option_names(self) -> list[str]:
        return [option.name for option in self.multi_select.options]


class DatabaseSelectProperty(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.SELECT
    select: DatabaseSelectConfig = Field(default_factory=DatabaseSelectConfig)

    @property
    def option_names(self) -> list[str]:
        return [option.name for option in self.select.options]


class DatabaseRelationProperty(BaseModel):
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
    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.DATE
    date: DatabaseDateConfig = Field(default_factory=DatabaseDateConfig)


class DatabaseTitleProperty(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.TITLE
    title: DatabaseTitleConfig = Field(default_factory=DatabaseTitleConfig)


class DatabaseRichTextProperty(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.RICH_TEXT
    rich_text: DatabaseRichTextConfig = Field(default_factory=DatabaseRichTextConfig)


class DatabaseURLProperty(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.URL
    url: DatabaseURLConfig = Field(default_factory=DatabaseURLConfig)


class DatabasePeopleProperty(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.PEOPLE
    people: DatabasePeopleConfig = Field(default_factory=DatabasePeopleConfig)


class DatabaseNumberProperty(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.NUMBER
    number: DatabaseNumberConfig = Field(default_factory=DatabaseNumberConfig)

    @property
    def number_format(self) -> str | None:
        return self.number.format


class DatabaseCheckboxProperty(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.CHECKBOX
    checkbox: DatabaseCheckboxConfig = Field(default_factory=DatabaseCheckboxConfig)


class DatabaseEmailProperty(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.EMAIL
    email: DatabaseEmailConfig = Field(default_factory=DatabaseEmailConfig)


class DatabasePhoneNumberProperty(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.PHONE_NUMBER
    phone_number: DatabasePhoneNumberConfig = Field(default_factory=DatabasePhoneNumberConfig)


class DatabaseCreatedTimeProperty(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.CREATED_TIME
    created_time: DatabaseCreatedTimeConfig = Field(default_factory=DatabaseCreatedTimeConfig)


# ===== TYPE UNION =====
DatabaseNotionProperty = (
    DatabaseStatusProperty
    | DatabaseMultiSelectProperty
    | DatabaseSelectProperty
    | DatabaseRelationProperty
    | DatabaseDateProperty
    | DatabaseTitleProperty
    | DatabaseRichTextProperty
    | DatabaseURLProperty
    | DatabasePeopleProperty
    | DatabaseNumberProperty
    | DatabaseCheckboxProperty
    | DatabaseEmailProperty
    | DatabasePhoneNumberProperty
    | DatabaseCreatedTimeProperty
    | dict[str, Any]  # Fallback
)

DatabasePropertyT = TypeVar("DatabasePropertyT", bound=DatabaseNotionProperty)


class NotionObjectWithDatabaseProperties(BaseModel, ABC):
    properties: dict[str, DatabaseNotionProperty] = Field(default_factory=dict)

    @field_validator("properties", mode="before")
    @classmethod
    def parse_database_properties(cls, value: dict[str, Any]) -> dict[str, DatabaseNotionProperty]:
        if not value:
            return {}

        return {key: cls._create_database_property(prop_data) for key, prop_data in value.items()}

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
