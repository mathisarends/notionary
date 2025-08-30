from pydantic import BaseModel
from typing import Literal, Optional

from notionary.blocks.models import Block
from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.blocks.types import BlockColor


class NumberedListItemBlock(BaseModel):
    rich_text: list[RichTextObject]
    color: BlockColor = BlockColor.DEFAULT
    children: Optional[list[Block]] = None


class CreateNumberedListItemBlock(BaseModel):
    type: Literal["numbered_list_item"] = "numbered_list_item"
    numbered_list_item: NumberedListItemBlock
