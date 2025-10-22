from pydantic import BaseModel

from notionary.page.properties.schemas import AnyPageProperty
from notionary.shared.entity.schemas import EntityResponseDto


class NotionPageDto(EntityResponseDto):
    archived: bool
    properties: dict[str, AnyPageProperty]


class PgePropertiesUpdateDto(BaseModel):
    properties: dict[str, AnyPageProperty]
