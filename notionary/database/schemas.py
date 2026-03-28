from uuid import UUID

from pydantic import BaseModel, Field

from notionary.rich_text.schemas import RichText
from notionary.shared.object.dtos import NotionObjectResponseDto, NotionObjectUpdateDto


class DataSourceReference(BaseModel):
    id: UUID
    name: str


class DatabaseDto(NotionObjectResponseDto):
    title: list[RichText] = Field(default_factory=list)
    description: list[RichText] = Field(default_factory=list)
    is_inline: bool = False
    is_locked: bool = False
    data_sources: list[DataSourceReference] = Field(default_factory=list)
    public_url: str | None = None


class CreateDatabaseRequest(BaseModel):
    parent: dict
    title: list[RichText] = Field(default_factory=list)
    description: list[RichText] = Field(default_factory=list)
    is_inline: bool | None = None
    initial_data_source: dict | None = None
    icon: dict | None = None
    cover: dict | None = None


class UpdateDatabaseRequest(NotionObjectUpdateDto):
    title: list[RichText] | None = None
    description: list[RichText] | None = None
    is_inline: bool | None = None
    is_locked: bool | None = None
