from typing import Literal
from pydantic import BaseModel, Field
from notionary.blocks.shared.models import Block, BlockColor, RichTextObject


class QuoteBlock(BaseModel):
    rich_text: list[RichTextObject]
    color: BlockColor = "default"
    children: list[Block] = Field(default_factory=list)


class CreateQuoteBlock(BaseModel):
    type: Literal["quote"] = "quote"
    quote: QuoteBlock
