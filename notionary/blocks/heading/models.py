from typing import Literal

from pydantic import BaseModel

from notionary.blocks.rich_text.models import RichText
from notionary.blocks.schemas import Block
from notionary.blocks.types import BlockColor, BlockType


class HeadingBlock(BaseModel):
    rich_text: list[RichText]
    color: BlockColor = BlockColor.DEFAULT
    is_toggleable: bool = False
    children: list[Block] | None = None


class CreateHeading1Block(BaseModel):
    type: Literal[BlockType.HEADING_1] = BlockType.HEADING_1
    heading_1: HeadingBlock


class CreateHeading2Block(BaseModel):
    type: Literal[BlockType.HEADING_2] = BlockType.HEADING_2
    heading_2: HeadingBlock


class CreateHeading3Block(BaseModel):
    type: Literal[BlockType.HEADING_3] = BlockType.HEADING_3
    heading_3: HeadingBlock
