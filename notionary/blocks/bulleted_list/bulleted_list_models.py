from typing import Literal

from pydantic import BaseModel, Field

from notionary.blocks.models import Block
from notionary.blocks.rich_text import RichTextObject
from notionary.blocks.types import BlockColor


class BulletedListItemBlock(BaseModel):
    rich_text: list[RichTextObject]
    color: BlockColor = BlockColor.DEFAULT


class CreateBulletedListItemBlock(BaseModel):
    type: Literal["bulleted_list_item"] = "bulleted_list_item"
    bulleted_list_item: BulletedListItemBlock
