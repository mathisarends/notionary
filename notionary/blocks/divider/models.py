from typing import Literal

from pydantic import BaseModel

from notionary.blocks.types import BlockType


class DividerBlock(BaseModel):
    pass


class CreateDividerBlock(BaseModel):
    type: Literal[BlockType.DIVIDER] = BlockType.DIVIDER
    divider: DividerBlock
