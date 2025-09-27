from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TypeVar

from pydantic import BaseModel, Field

from notionary.shared.models.shared_property_models import PropertyType


class DataSourcePropertyOption(BaseModel):
    id: str
    name: str
    color: str
    description: str | None = None


class DataSourceStatusGroup(BaseModel):
    id: str
    name: str
    color: str
    option_ids: list[str]


# This class has no mapping to the api but is a convenient wrapper to display options of status props
@dataclass
class EnrichedDataSourceStatusOption:
    id: str
    name: str
    color: str
    description: str | None = None
    group_name: str | None = None


class DataSourceStatusConfig(BaseModel):
    options: list[DataSourcePropertyOption] = Field(default_factory=list)
    groups: list[DataSourceStatusGroup] = Field(default_factory=list)

    @property
    def detailed_options(self) -> list[EnrichedDataSourceStatusOption]:
        option_to_group = {option_id: group.name for group in self.groups for option_id in group.option_ids}

        return [
            EnrichedDataSourceStatusOption(
                id=option.id,
                name=option.name,
                color=option.color,
                description=option.description,
                group_name=option_to_group.get(option.id),
            )
            for option in self.options
        ]


class DataSourceSelectConfig(BaseModel):
    options: list[DataSourcePropertyOption] = Field(default_factory=list)


class DataSourceMultiSelectConfig(BaseModel):
    options: list[DataSourcePropertyOption] = Field(default_factory=list)


class DataSourceRelationConfig(BaseModel):
    database_id: str | None = None
    data_source_id: str | None = None
    type: str = "single_property"
    single_property: dict[str, Any] = Field(default_factory=dict)


# Simple empty config classes for basic property types (these dont define a schema and therefore are of no further interest to this api)
class DataSourceDateConfig(BaseModel): ...


class DataSourceTitleConfig(BaseModel): ...


class DataSourceRichTextConfig(BaseModel): ...


class DataSourceURLConfig(BaseModel): ...


class DataSourcePeopleConfig(BaseModel): ...


class DataSourceCheckboxConfig(BaseModel): ...


class DataSourceEmailConfig(BaseModel): ...


class DataSourcePhoneNumberConfig(BaseModel): ...


class DataSourceCreatedTimeConfig(BaseModel): ...


# Config classes with actual fields
class DataSourceNumberConfig(BaseModel):
    format: str | None = None  # e.g., "number", "number_with_commas", "percent", etc.


class DataSourceStatusProperty(BaseModel):
    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.STATUS
    status: DataSourceStatusConfig = Field(default_factory=DataSourceStatusConfig)

    @property
    def option_names(self) -> list[str]:
        return [option.name for option in self.status.options]

    @property
    def group_names(self) -> list[str]:
        return [group.name for group in self.status.groups]


class DataSourceMultiSelectProperty(BaseModel):
    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.MULTI_SELECT
    multi_select: DataSourceMultiSelectConfig = Field(default_factory=DataSourceMultiSelectConfig)

    @property
    def option_names(self) -> list[str]:
        return [option.name for option in self.multi_select.options]


class DataSourceSelectProperty(BaseModel):
    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.SELECT
    select: DataSourceSelectConfig = Field(default_factory=DataSourceSelectConfig)

    @property
    def option_names(self) -> list[str]:
        return [option.name for option in self.select.options]


class DataSourceRelationProperty(BaseModel):
    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.RELATION
    relation: DataSourceRelationConfig = Field(default_factory=DataSourceRelationConfig)

    @property
    def related_database_id(self) -> str:
        return self.relation.database_id

    @property
    def related_data_source_id(self) -> str:
        return self.relation.data_source_id


class DataSourceDateProperty(BaseModel):
    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.DATE
    date: DataSourceDateConfig = Field(default_factory=DataSourceDateConfig)


class DataSourceTitleProperty(BaseModel):
    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.TITLE
    title: DataSourceTitleConfig = Field(default_factory=DataSourceTitleConfig)


class DataSourceRichTextProperty(BaseModel):
    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.RICH_TEXT
    rich_text: DataSourceRichTextConfig = Field(default_factory=DataSourceRichTextConfig)


class DataSourceURLProperty(BaseModel):
    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.URL
    url: DataSourceURLConfig = Field(default_factory=DataSourceURLConfig)


class DataSourcePeopleProperty(BaseModel):
    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.PEOPLE
    people: DataSourcePeopleConfig = Field(default_factory=DataSourcePeopleConfig)


class DataSourceNumberProperty(BaseModel):
    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.NUMBER
    number: DataSourceNumberConfig = Field(default_factory=DataSourceNumberConfig)

    @property
    def number_format(self) -> str | None:
        return self.number.format


class DataSourceCheckboxProperty(BaseModel):
    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.CHECKBOX
    checkbox: DataSourceCheckboxConfig = Field(default_factory=DataSourceCheckboxConfig)


class DataSourceEmailProperty(BaseModel):
    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.EMAIL
    email: DataSourceEmailConfig = Field(default_factory=DataSourceEmailConfig)


class DataSourcePhoneNumberProperty(BaseModel):
    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.PHONE_NUMBER
    phone_number: DataSourcePhoneNumberConfig = Field(default_factory=DataSourcePhoneNumberConfig)


class DataSourceCreatedTimeProperty(BaseModel):
    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.CREATED_TIME
    created_time: DataSourceCreatedTimeConfig = Field(default_factory=DataSourceCreatedTimeConfig)


DataSourceNotionProperty = (
    DataSourceStatusProperty
    | DataSourceMultiSelectProperty
    | DataSourceSelectProperty
    | DataSourceRelationProperty
    | DataSourceDateProperty
    | DataSourceTitleProperty
    | DataSourceRichTextProperty
    | DataSourceURLProperty
    | DataSourcePeopleProperty
    | DataSourceNumberProperty
    | DataSourceCheckboxProperty
    | DataSourceEmailProperty
    | DataSourcePhoneNumberProperty
    | DataSourceCreatedTimeProperty
    | dict[str, Any]  # Fallback
)

DataSourcePropertyT = TypeVar("DataSourcePropertyT", bound=DataSourceNotionProperty)
