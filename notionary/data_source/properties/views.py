from pydantic import BaseModel, ConfigDict, Field

from notionary.data_source.properties.schemas import NumberFormat
from notionary.shared.properties.type import PropertyType


class DataSourceRelationOption(BaseModel):
    """A relation target represented by id and human-readable title."""

    id: str
    title: str | None = None


class DataSourcePropertyDescription(BaseModel):
    """Normalized description of a single data source property."""

    type: PropertyType | str
    options: list[str] = Field(default_factory=list)
    groups: list[str] = Field(default_factory=list)
    format: NumberFormat | str | None = None
    relation_options: list[DataSourceRelationOption] = Field(default_factory=list)


class _RawOptionName(BaseModel):
    name: str


class _RawGroupName(BaseModel):
    name: str


class _RawStatusConfig(BaseModel):
    options: list[_RawOptionName] = Field(default_factory=list)
    groups: list[_RawGroupName] = Field(default_factory=list)


class _RawSelectConfig(BaseModel):
    options: list[_RawOptionName] = Field(default_factory=list)


class _RawNumberConfig(BaseModel):
    format: NumberFormat | str


class _RawRelationConfig(BaseModel):
    model_config = ConfigDict(extra="allow")

    data_source_id: str | None = None
    data_source_name: str | None = None
    database_id: str | None = None
    database_name: str | None = None


class RawDataSourceProperty(BaseModel):
    model_config = ConfigDict(extra="allow")

    type: PropertyType | str
    status: _RawStatusConfig | None = None
    select: _RawSelectConfig | None = None
    multi_select: _RawSelectConfig | None = None
    number: _RawNumberConfig | None = None
    relation: _RawRelationConfig | None = None
