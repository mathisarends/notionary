from typing import Literal

from pydantic import BaseModel

from notionary.blocks.rich_text.models import RichText
from notionary.data_source.properties.models import DiscriminatedDataSourceProperty
from notionary.page.page_models import NotionPageDto
from notionary.shared.entity.entity_models import EntityDto, NotionEntityUpdateDto
from notionary.shared.entity.user_context_mixin import UserContextMixin
from notionary.shared.models.parent_models import Parent


class UpdateDataSourceDto(NotionEntityUpdateDto):
    title: list[RichText]
    description: list[RichText]
    archived: bool


class QueryDataSourceResponse(BaseModel):
    object: Literal["list"]
    results: list[NotionPageDto]
    next_cursor: str | None = None
    has_more: bool


class DataSourceDto(EntityDto, UserContextMixin):
    database_parent: Parent
    title: list[RichText]
    description: list[RichText]
    archived: bool
    properties: dict[str, DiscriminatedDataSourceProperty]
