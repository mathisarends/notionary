from typing import Literal

from pydantic import BaseModel

from notionary.blocks.rich_text.rich_text_models import RichText
from notionary.blocks.types import BlockColor, BlockType


class BulletedListItemBlock(BaseModel):
    rich_text: list[RichText]
    color: BlockColor = BlockColor.DEFAULT


class CreateBulletedListItemBlock(BaseModel):
    type: Literal[BlockType.BULLETED_LIST_ITEM] = BlockType.BULLETED_LIST_ITEM
    bulleted_list_item: BulletedListItemBlock
