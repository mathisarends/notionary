from typing import Any

from pydantic import BaseModel, Field, field_validator

from notionary.database.properties.database_property_models import (
    DatabaseCheckboxProperty,
    DatabaseCreatedTimeProperty,
    DatabaseDateProperty,
    DatabaseEmailProperty,
    DatabaseMultiSelectProperty,
    DatabaseNotionProperty,
    DatabaseNumberProperty,
    DatabasePeopleProperty,
    DatabasePhoneNumberProperty,
    DatabaseRelationProperty,
    DatabaseRichTextProperty,
    DatabaseSelectProperty,
    DatabaseStatusProperty,
    DatabaseTitleProperty,
    DatabaseURLProperty,
)
from notionary.shared.models.shared_property_models import PropertyType


class DatabasePropertiesMixin(BaseModel):
    properties: dict[str, DatabaseNotionProperty] = Field(default_factory=dict)

    @field_validator("properties", mode="before")
    @classmethod
    def parse_database_properties(cls, property_values: dict[str, Any]) -> dict[str, DatabaseNotionProperty]:
        if not property_values:
            return {}

        return {key: cls._create_database_property(prop_data) for key, prop_data in property_values.items()}

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
            result = property_class(**prop_data)
            return result

        return prop_data
