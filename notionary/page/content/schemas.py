from enum import StrEnum
from typing import Self

from pydantic import BaseModel


class MarkdownCommandType(StrEnum):
    INSERT_CONTENT = "insert_content"
    REPLACE_CONTENT = "replace_content"
    UPDATE_CONTENT = "update_content"
    REPLACE_CONTENT_RANGE = "replace_content_range"


class PageMarkdownResponse(BaseModel):
    object: str
    id: str
    markdown: str
    truncated: bool
    unknown_block_ids: list[str]


class _InsertContentBody(BaseModel):
    content: str


class InsertContentRequest(BaseModel):
    type: MarkdownCommandType = MarkdownCommandType.INSERT_CONTENT
    insert_content: _InsertContentBody

    @classmethod
    def from_markdown(cls, content: str) -> Self:
        return cls(insert_content=_InsertContentBody(content=content))


class _ReplaceContentBody(BaseModel):
    new_str: str


class ReplaceContentRequest(BaseModel):
    type: MarkdownCommandType = MarkdownCommandType.REPLACE_CONTENT
    replace_content: _ReplaceContentBody

    @classmethod
    def from_markdown(cls, content: str) -> Self:
        return cls(replace_content=_ReplaceContentBody(new_str=content))
