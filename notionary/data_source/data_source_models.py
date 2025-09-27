from typing import Literal

from pydantic import BaseModel

from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.data_source.properties.data_source_properties_mixin import DataSourcePropertiesMixin
from notionary.shared.entity.entity_models import EntityDto
from notionary.shared.entity.user_context_mixin import UserContextMixin
from notionary.shared.models.parent_models import NotionParent


class DataSourceDto(EntityDto, UserContextMixin, DataSourcePropertiesMixin):
    database_parent: NotionParent
    title: list[RichTextObject]
    description: list[RichTextObject]
    archived: bool


class DataSourceSearchResponse(BaseModel):
    results: list[DataSourceDto]
    next_cursor: str | None = None
    has_more: bool
    type: Literal["page_or_data_source"]
