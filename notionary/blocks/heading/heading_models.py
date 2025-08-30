from typing import Literal, Optional

from pydantic import BaseModel

from notionary.blocks.models import Block
from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.blocks.types import BlockColor


class HeadingBlock(BaseModel):
    rich_text: list[RichTextObject]
    color: BlockColor = BlockColor.DEFAULT
    is_toggleable: bool = False
    children: Optional[list[Block]] = None


class CreateHeading1Block(BaseModel):
    type: Literal["heading_1"] = "heading_1"
    heading_1: HeadingBlock


class CreateHeading2Block(BaseModel):
    type: Literal["heading_2"] = "heading_2"
    heading_2: HeadingBlock


class CreateHeading3Block(BaseModel):
    type: Literal["heading_3"] = "heading_3"
    heading_3: HeadingBlock
