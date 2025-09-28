from enum import StrEnum

from pydantic import BaseModel, Field

from notionary.shared.models.shared_property_models import PropertyType


class PropertyColor(StrEnum):
    DEFAULT = "default"
    GRAY = "gray"
    BROWN = "brown"
    ORANGE = "orange"
    YELLOW = "yellow"
    GREEN = "green"
    BLUE = "blue"
    PURPLE = "purple"
    PINK = "pink"
    RED = "red"


class DataSourcePropertyOption(BaseModel):
    id: str
    name: str
    color: PropertyColor
    description: str | None = None


class DataSourceStatusGroup(BaseModel):
    id: str
    name: str
    color: PropertyColor
    option_ids: list[str]


class DataSourceStatusConfig(BaseModel):
    options: list[DataSourcePropertyOption] = Field(default_factory=list)
    groups: list[DataSourceStatusGroup] = Field(default_factory=list)


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
