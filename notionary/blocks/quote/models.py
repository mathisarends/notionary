from typing import Literal

from pydantic import BaseModel, Field

from notionary.blocks.rich_text.models import RichText
from notionary.blocks.schemas import Block
from notionary.blocks.types import BlockColor, BlockType


class QuoteBlock(BaseModel):
    rich_text: list[RichText]
    color: BlockColor = BlockColor.DEFAULT
    children: list[Block] = Field(default_factory=list)


class CreateQuoteBlock(BaseModel):
    type: Literal[BlockType.QUOTE] = BlockType.QUOTE
    quote: QuoteBlock
