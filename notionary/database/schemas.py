from pydantic import BaseModel, Field

from notionary.blocks.rich_text.models import RichText
from notionary.shared.entity.schemas import EntityResponseDto
from notionary.shared.models.file import File
from notionary.shared.models.icon import Icon


class _DataSourceDiscoveryDto(BaseModel):
    id: str
    name: str


class NotionDatabaseDto(EntityResponseDto):
    title: list[RichText]
    description: list[RichText]
    is_inline: bool
    is_locked: bool
    data_sources: list[_DataSourceDiscoveryDto] = Field(default_factory=list)
    url: str
    public_url: str | None = None


class NotionDatabaseUpdateDto(BaseModel):
    title: list[RichText] | None = None
    icon: Icon | None = None
    cover: File | None = None
    archived: bool | None = None
    description: list[RichText] | None = None
