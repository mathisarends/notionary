from typing import Literal

from pydantic import BaseModel, Field

from notionary.blocks.rich_text.rich_text_models import RichText
from notionary.blocks.types import BlockType


class BookmarkBlock(BaseModel):
    caption: list[RichText] = Field(default_factory=list)
    url: str


class CreateBookmarkBlock(BaseModel):
    type: Literal[BlockType.BOOKMARK] = BlockType.BOOKMARK
    bookmark: BookmarkBlock
