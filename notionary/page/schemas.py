from pydantic import BaseModel

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
