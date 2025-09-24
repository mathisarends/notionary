from typing import Any

from pydantic import BaseModel, Field, field_validator

from notionary.page.properties.page_property_models import (
    PageCheckboxProperty,
    PageCreatedTimeProperty,
    PageDateProperty,
    PageEmailProperty,
    PageMultiSelectProperty,
    PageNumberProperty,
    PagePeopleProperty,
    PagePhoneNumberProperty,
    PageProperty,
    PageRelationProperty,
    PageRichTextProperty,
    PageSelectProperty,
    PageStatusProperty,
    PageTitleProperty,
    PageURLProperty,
)
from notionary.shared.models.shared_property_models import PropertyType


class PagePropertiesMixin(BaseModel):
    properties: dict[str, PageProperty] = Field(default_factory=dict)

    @field_validator("properties", mode="before")
    @classmethod
    def parse_properties(cls, v: dict[str, Any]) -> dict[str, PageProperty]:
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
            result = property_class(**prop_data)
            return result

        return prop_data
