from pydantic import BaseModel

from notionary.page.properties.page_property_models import DiscriminatedPageProperty
from notionary.shared.entity.entity_models import EntityDto
from notionary.shared.entity.user_context_mixin import UserContextMixin


class NotionPageDto(EntityDto, UserContextMixin):
    archived: bool
    properties: dict[str, DiscriminatedPageProperty]


class PgePropertiesUpdateDto(BaseModel):
    properties: dict[str, DiscriminatedPageProperty]
