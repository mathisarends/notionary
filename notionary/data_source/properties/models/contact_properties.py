from pydantic import BaseModel, Field

from notionary.shared.properties.property_type import PropertyType


class DataSourceEmailConfig(BaseModel): ...


class DataSourcePhoneNumberConfig(BaseModel): ...


class DataSourcePeopleConfig(BaseModel): ...


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


class DataSourcePeopleProperty(BaseModel):
    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.PEOPLE
    people: DataSourcePeopleConfig = Field(default_factory=DataSourcePeopleConfig)
