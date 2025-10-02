from typing import Literal

from pydantic import BaseModel, Field

from notionary.blocks.models import Block
from notionary.blocks.rich_text.models import RichText
from notionary.blocks.types import BlockColor, BlockType


class ToggleBlock(BaseModel):
    rich_text: list[RichText]
    color: BlockColor = BlockColor.DEFAULT
    children: list[Block] = Field(default_factory=list)


class CreateToggleBlock(BaseModel):
    type: Literal[BlockType.TOGGLE] = BlockType.TOGGLE
    toggle: ToggleBlock
