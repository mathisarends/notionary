from abc import abstractmethod
from typing import Any, TypeVar

from pydantic import BaseModel, Field, field_validator

from notionary.shared.properties.property_type import PropertyType

PropertyT = TypeVar("PropertyT")


class BasePropertyMixin[PropertyT](BaseModel):
    properties: dict[str, PropertyT] = Field(default_factory=dict)

    @field_validator("properties", mode="before")
    @classmethod
    def parse_properties(cls, v: dict[str, Any]) -> dict[str, PropertyT]:
        if not v:
            return {}

        return {key: cls._create_property(prop_data) for key, prop_data in v.items()}

    @classmethod
    @abstractmethod
    def _get_property_classes(cls) -> dict[PropertyType, type[PropertyT]]:
        pass

    @classmethod
    def _create_property(cls, prop_data: Any) -> PropertyT:
        if not isinstance(prop_data, dict) or "type" not in prop_data:
            return prop_data

        prop_type = prop_data.get("type")
        property_classes = cls._get_property_classes()
        property_class = property_classes.get(prop_type)

        if property_class:
            return property_class(**prop_data)

        return prop_data
