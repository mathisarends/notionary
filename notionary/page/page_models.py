from pydantic import BaseModel

from notionary.page.properties.models import DiscriminatedPageProperty
from notionary.shared.entity.schemas import EntityResponseDto


class NotionPageDto(EntityResponseDto):
    archived: bool
    properties: dict[str, DiscriminatedPageProperty]


class PgePropertiesUpdateDto(BaseModel):
    properties: dict[str, DiscriminatedPageProperty]
