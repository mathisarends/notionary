from pydantic import BaseModel, Field

from notionary.shared.properties.property_type import PropertyType

from .status_properties import DataSourcePropertyOption


class DataSourceSelectConfig(BaseModel):
    options: list[DataSourcePropertyOption] = Field(default_factory=list)


class DataSourceMultiSelectConfig(BaseModel):
    options: list[DataSourcePropertyOption] = Field(default_factory=list)


class DataSourceSelectProperty(BaseModel):
    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.SELECT
    select: DataSourceSelectConfig = Field(default_factory=DataSourceSelectConfig)

    @property
    def option_names(self) -> list[str]:
        return [option.name for option in self.select.options]


class DataSourceMultiSelectProperty(BaseModel):
    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.MULTI_SELECT
    multi_select: DataSourceMultiSelectConfig = Field(default_factory=DataSourceMultiSelectConfig)

    @property
    def option_names(self) -> list[str]:
        return [option.name for option in self.multi_select.options]
