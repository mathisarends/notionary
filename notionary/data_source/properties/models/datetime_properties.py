from pydantic import BaseModel, Field

from notionary.shared.models.shared_property_models import PropertyType


class DataSourceDateConfig(BaseModel): ...


class DataSourceCreatedTimeConfig(BaseModel): ...


class DataSourceCreatedByConfig(BaseModel): ...


class DataSourceLastEditedByConfig(BaseModel): ...


class DataSourceLastVisitedTimeConfig(BaseModel): ...


class DataSourceDateProperty(BaseModel):
    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.DATE
    date: DataSourceDateConfig = Field(default_factory=DataSourceDateConfig)


class DataSourceCreatedTimeProperty(BaseModel):
    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.CREATED_TIME
    created_time: DataSourceCreatedTimeConfig = Field(default_factory=DataSourceCreatedTimeConfig)
