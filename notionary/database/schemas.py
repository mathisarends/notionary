from pydantic import BaseModel, Field

from notionary.rich_text.schemas import RichText
from notionary.shared.models.file import File
from notionary.shared.models.icon import Icon
from notionary.shared.models.parent import Parent


class DataSourceReference(BaseModel):
    id: str
    name: str


class DatabaseDto(BaseModel):
    object: str
    id: str
    title: list[RichText] = Field(default_factory=list)
    description: list[RichText] = Field(default_factory=list)
    parent: Parent | None = None
    is_inline: bool = False
    in_trash: bool = False
    is_locked: bool = False
    created_time: str | None = None
    last_edited_time: str | None = None
    data_sources: list[DataSourceReference] = Field(default_factory=list)
    icon: Icon | None = None
    cover: File | None = None
    url: str = ""
    public_url: str | None = None


class CreateDatabaseRequest(BaseModel):
    parent: dict
    title: list[RichText] = Field(default_factory=list)
    description: list[RichText] = Field(default_factory=list)
    is_inline: bool | None = None
    initial_data_source: dict | None = None
    icon: dict | None = None
    cover: dict | None = None


class UpdateDatabaseRequest(BaseModel):
    title: list[RichText] | None = None
    description: list[RichText] | None = None
    is_inline: bool | None = None
    icon: Icon | None = None
    cover: File | None = None
    in_trash: bool | None = None
    is_locked: bool | None = None
