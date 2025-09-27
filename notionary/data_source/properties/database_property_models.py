from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from notionary.shared.models.shared_property_models import PropertyType


class IgnoreExtraFieldsMixin(BaseModel):
    model_config = ConfigDict(extra="ignore")


class DatabasePropertyOption(IgnoreExtraFieldsMixin):
    id: str
    name: str
    color: str
    description: str | None = None


class DatabaseStatusGroup(IgnoreExtraFieldsMixin):
    id: str
    name: str
    color: str
    option_ids: list[str]


# This class has no mapping to the api but is a convenient wrapper to display options of status props
@dataclass
class EnrichedDatabaseStatusOption:
    id: str
    name: str
    color: str
    description: str | None = None
    group_name: str | None = None


class DatabaseStatusConfig(IgnoreExtraFieldsMixin):
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


class DatabaseSelectConfig(IgnoreExtraFieldsMixin):
    options: list[DatabasePropertyOption] = Field(default_factory=list)


class DatabaseMultiSelectConfig(IgnoreExtraFieldsMixin):
    options: list[DatabasePropertyOption] = Field(default_factory=list)


class DatabaseRelationConfig(IgnoreExtraFieldsMixin):
    database_id: str | None = None
    data_source_id: str | None = None
    type: str = "single_property"
    single_property: dict[str, Any] = Field(default_factory=dict)


# Simple empty config classes for basic property types (these dont define a schema and therefore are of no further interest to this api)
class DatabaseDateConfig(IgnoreExtraFieldsMixin): ...


class DatabaseTitleConfig(IgnoreExtraFieldsMixin): ...


class DatabaseRichTextConfig(IgnoreExtraFieldsMixin): ...


class DatabaseURLConfig(IgnoreExtraFieldsMixin): ...


class DatabasePeopleConfig(IgnoreExtraFieldsMixin): ...


class DatabaseCheckboxConfig(IgnoreExtraFieldsMixin): ...


class DatabaseEmailConfig(IgnoreExtraFieldsMixin): ...


class DatabasePhoneNumberConfig(IgnoreExtraFieldsMixin): ...


class DatabaseCreatedTimeConfig(IgnoreExtraFieldsMixin): ...


# Config classes with actual fields
class DatabaseNumberConfig(IgnoreExtraFieldsMixin):
    format: str | None = None  # e.g., "number", "number_with_commas", "percent", etc.


class DatabaseStatusProperty(IgnoreExtraFieldsMixin):
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


class DatabaseMultiSelectProperty(IgnoreExtraFieldsMixin):
    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.MULTI_SELECT
    multi_select: DatabaseMultiSelectConfig = Field(default_factory=DatabaseMultiSelectConfig)

    @property
    def option_names(self) -> list[str]:
        return [option.name for option in self.multi_select.options]


class DatabaseSelectProperty(IgnoreExtraFieldsMixin):
    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.SELECT
    select: DatabaseSelectConfig = Field(default_factory=DatabaseSelectConfig)

    @property
    def option_names(self) -> list[str]:
        return [option.name for option in self.select.options]


class DatabaseRelationProperty(IgnoreExtraFieldsMixin):
    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.RELATION
    relation: DatabaseRelationConfig = Field(default_factory=DatabaseRelationConfig)

    @property
    def related_database_id(self) -> str:
        """Get the related database ID."""
        return self.relation.database_id


class DatabaseDateProperty(IgnoreExtraFieldsMixin):
    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.DATE
    date: DatabaseDateConfig = Field(default_factory=DatabaseDateConfig)


class DatabaseTitleProperty(IgnoreExtraFieldsMixin):
    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.TITLE
    title: DatabaseTitleConfig = Field(default_factory=DatabaseTitleConfig)


class DatabaseRichTextProperty(IgnoreExtraFieldsMixin):
    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.RICH_TEXT
    rich_text: DatabaseRichTextConfig = Field(default_factory=DatabaseRichTextConfig)


class DatabaseURLProperty(IgnoreExtraFieldsMixin):
    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.URL
    url: DatabaseURLConfig = Field(default_factory=DatabaseURLConfig)


class DatabasePeopleProperty(IgnoreExtraFieldsMixin):
    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.PEOPLE
    people: DatabasePeopleConfig = Field(default_factory=DatabasePeopleConfig)


class DatabaseNumberProperty(IgnoreExtraFieldsMixin):
    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.NUMBER
    number: DatabaseNumberConfig = Field(default_factory=DatabaseNumberConfig)

    @property
    def number_format(self) -> str | None:
        return self.number.format


class DatabaseCheckboxProperty(IgnoreExtraFieldsMixin):
    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.CHECKBOX
    checkbox: DatabaseCheckboxConfig = Field(default_factory=DatabaseCheckboxConfig)


class DatabaseEmailProperty(IgnoreExtraFieldsMixin):
    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.EMAIL
    email: DatabaseEmailConfig = Field(default_factory=DatabaseEmailConfig)


class DatabasePhoneNumberProperty(IgnoreExtraFieldsMixin):
    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.PHONE_NUMBER
    phone_number: DatabasePhoneNumberConfig = Field(default_factory=DatabasePhoneNumberConfig)


class DatabaseCreatedTimeProperty(IgnoreExtraFieldsMixin):
    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.CREATED_TIME
    created_time: DatabaseCreatedTimeConfig = Field(default_factory=DatabaseCreatedTimeConfig)


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
