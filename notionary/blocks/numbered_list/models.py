from typing import Literal

from pydantic import BaseModel

from notionary.blocks.models import Block
from notionary.blocks.rich_text.models import RichText
from notionary.blocks.types import BlockColor, BlockType


class NumberedListItemBlock(BaseModel):
    rich_text: list[RichText]
    color: BlockColor = BlockColor.DEFAULT
    children: list[Block] | None = None


class CreateNumberedListItemBlock(BaseModel):
    type: Literal[BlockType.NUMBERED_LIST_ITEM] = BlockType.NUMBERED_LIST_ITEM
    numbered_list_item: NumberedListItemBlock
