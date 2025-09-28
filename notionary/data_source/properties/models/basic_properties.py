from pydantic import BaseModel, Field

from notionary.shared.properties.property_type import PropertyType


class DataSourceCheckboxConfig(BaseModel): ...


class DataSourceButtonConfig(BaseModel): ...


class DataSourceLocationConfig(BaseModel): ...


class DataSourceVerificationConfig(BaseModel): ...


class DataSourcePlaceConfig(BaseModel): ...


class DataSourceCheckboxProperty(BaseModel):
    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.CHECKBOX
    checkbox: DataSourceCheckboxConfig = Field(default_factory=DataSourceCheckboxConfig)
