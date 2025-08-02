from typing import Literal
from pydantic import BaseModel, Field
from notionary.blocks.shared.models import BlockColor, RichTextObject
from notionary.models.notion_block_response import Block


class HeadingBlock(BaseModel):
    rich_text: list[RichTextObject]
    color: BlockColor = "default"
    is_toggleable: bool = False
    children: list[Block] = Field(default_factory=list)


class CreateHeading1Block(BaseModel):
    type: Literal["heading_1"] = "heading_1"
    heading_1: HeadingBlock


class CreateHeading2Block(BaseModel):
    type: Literal["heading_2"] = "heading_2"
    heading_2: HeadingBlock


class CreateHeading3Block(BaseModel):
    type: Literal["heading_3"] = "heading_3"
    heading_3: HeadingBlock
