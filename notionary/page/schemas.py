from typing import Annotated, Literal

from pydantic import BaseModel, Field

from notionary.page.properties.schemas import AnyPageProperty
from notionary.shared.entity.schemas import EntityResponseDto


class PageDto(EntityResponseDto):
    properties: dict[str, AnyPageProperty]


class PgePropertiesUpdateDto(BaseModel):
    properties: dict[str, AnyPageProperty]


class _InsertContentBody(BaseModel):
    content: str


class InsertContentRequest(BaseModel):
    type: str = "insert_content"
    insert_content: _InsertContentBody


class _ReplaceContentBody(BaseModel):
    new_str: str


class ReplaceContentRequest(BaseModel):
    type: str = "replace_content"
    replace_content: _ReplaceContentBody


class _DefaultTemplate(BaseModel):
    type: Literal["default"] = "default"
    timezone: str | None = None


class _TemplateById(BaseModel):
    type: Literal["template_id"] = "template_id"
    template_id: str
    timezone: str | None = None


PageTemplate = Annotated[_DefaultTemplate | _TemplateById, Field(discriminator="type")]


class PageUpdateRequest(BaseModel):
    erase_content: bool | None = None
    is_locked: bool | None = None
    template: PageTemplate | None = None
    in_trash: bool | None = None
