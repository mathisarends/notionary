from typing import Any

from pydantic import BaseModel, Field, field_validator

from notionary.data_source.properties.data_source_property_models import (
    DataSourceCheckboxProperty,
    DataSourceCreatedTimeProperty,
    DataSourceDateProperty,
    DataSourceEmailProperty,
    DataSourceMultiSelectProperty,
    DataSourceNotionProperty,
    DataSourceNumberProperty,
    DataSourcePeopleProperty,
    DataSourcePhoneNumberProperty,
    DataSourceRelationProperty,
    DataSourceRichTextProperty,
    DataSourceSelectProperty,
    DataSourceStatusProperty,
    DataSourceTitleProperty,
    DataSourceURLProperty,
)
from notionary.shared.models.shared_property_models import PropertyType


class DataSourcePropertiesMixin(BaseModel):
    properties: dict[str, DataSourceNotionProperty] = Field(default_factory=dict)

    @field_validator("properties", mode="before")
    @classmethod
    def parse_data_source_properties(cls, property_values: dict[str, Any]) -> dict[str, DataSourceNotionProperty]:
        if not property_values:
            return {}

        return {key: cls.create_typed_data_source_property(prop_data) for key, prop_data in property_values.items()}

    @classmethod
    def create_typed_data_source_property(cls, prop_data: Any) -> DataSourceNotionProperty:
        if not isinstance(prop_data, dict) or "type" not in prop_data:
            return prop_data

        prop_type = prop_data.get("type")

        data_source_property_classes = {
            PropertyType.STATUS: DataSourceStatusProperty,
            PropertyType.MULTI_SELECT: DataSourceMultiSelectProperty,
            PropertyType.SELECT: DataSourceSelectProperty,
            PropertyType.RELATION: DataSourceRelationProperty,
            PropertyType.DATE: DataSourceDateProperty,
            PropertyType.TITLE: DataSourceTitleProperty,
            PropertyType.RICH_TEXT: DataSourceRichTextProperty,
            PropertyType.URL: DataSourceURLProperty,
            PropertyType.PEOPLE: DataSourcePeopleProperty,
            PropertyType.NUMBER: DataSourceNumberProperty,
            PropertyType.CHECKBOX: DataSourceCheckboxProperty,
            PropertyType.EMAIL: DataSourceEmailProperty,
            PropertyType.PHONE_NUMBER: DataSourcePhoneNumberProperty,
            PropertyType.CREATED_TIME: DataSourceCreatedTimeProperty,
        }

        property_class = data_source_property_classes.get(prop_type)

        if property_class:
            result = property_class(**prop_data)
            return result

        return prop_data
