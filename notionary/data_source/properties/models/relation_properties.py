from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from notionary.shared.models.shared_property_models import PropertyType


class RelationType(StrEnum):
    SINGLE_PROPERTY = "single_property"
    DUAL_PROPERTY = "dual_property"


class DataSourceRelationConfig(BaseModel):
    database_id: str | None = None
    data_source_id: str | None = None
    type: RelationType = RelationType.SINGLE_PROPERTY
    single_property: dict[str, Any] = Field(default_factory=dict)


class DataSourceRelationProperty(BaseModel):
    id: str
    name: str
    description: str | None = None
    type: PropertyType = PropertyType.RELATION
    relation: DataSourceRelationConfig = Field(default_factory=DataSourceRelationConfig)

    @property
    def related_database_id(self) -> str:
        return self.relation.database_id

    @property
    def related_data_source_id(self) -> str:
        return self.relation.data_source_id
