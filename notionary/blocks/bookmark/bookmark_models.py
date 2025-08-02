from typing import Literal
from pydantic import BaseModel, Field

from notionary.blocks.rich_text.rich_text_models import RichTextObject


class BookmarkBlock(BaseModel):
    caption: list[RichTextObject] = Field(default_factory=list)
    url: str


class CreateBookmarkBlock(BaseModel):
    type: Literal["bookmark"] = "bookmark"
    bookmark: BookmarkBlock
