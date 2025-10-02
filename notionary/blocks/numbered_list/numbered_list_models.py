from typing import Literal

from pydantic import BaseModel

from notionary.blocks.models import Block
from notionary.blocks.rich_text.rich_text_models import RichText
from notionary.blocks.types import BlockColor


class NumberedListItemBlock(BaseModel):
    rich_text: list[RichText]
    color: BlockColor = BlockColor.DEFAULT
    children: list[Block] | None = None


class CreateNumberedListItemBlock(BaseModel):
    type: Literal["numbered_list_item"] = "numbered_list_item"
    numbered_list_item: NumberedListItemBlock
