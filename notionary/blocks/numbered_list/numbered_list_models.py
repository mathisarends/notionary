from typing_extensions import Literal
from pydantic import BaseModel, Field

from notionary.blocks.block_models import Block
from notionary.blocks.block_types import BlockColor
from notionary.blocks.rich_text.rich_text_models import RichTextObject


class NumberedListItemBlock(BaseModel):
    rich_text: list[RichTextObject]
    color: BlockColor = BlockColor.DEFAULT
    children: list[Block] = Field(default_factory=list)


class CreateNumberedListItemBlock(BaseModel):
    type: Literal["numbered_list_item"] = "numbered_list_item"
    numbered_list_item: NumberedListItemBlock
