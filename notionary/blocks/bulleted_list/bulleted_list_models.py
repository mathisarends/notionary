from typing import Literal

from pydantic import BaseModel, Field

from notionary.blocks.block_models import Block
from notionary.blocks.block_types import BlockColor
from notionary.blocks.rich_text.rich_text_models import RichTextObject


class BulletedListItemBlock(BaseModel):
    rich_text: list[RichTextObject]
    color: BlockColor = BlockColor.DEFAULT
    children: list[Block] = Field(default_factory=list)


class CreateBulletedListItemBlock(BaseModel):
    type: Literal["bulleted_list_item"] = "bulleted_list_item"
    bulleted_list_item: BulletedListItemBlock
