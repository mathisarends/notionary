from typing import Literal
from pydantic import BaseModel, Field
from notionary.blocks.block_models import Block, BlockColor
from notionary.blocks.rich_text.rich_text_models import RichTextObject


class QuoteBlock(BaseModel):
    rich_text: list[RichTextObject]
    color: BlockColor = BlockColor.DEFAULT
    children: list[Block] = Field(default_factory=list)


class CreateQuoteBlock(BaseModel):
    type: Literal["quote"] = "quote"
    quote: QuoteBlock
