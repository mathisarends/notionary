from typing import Literal

from pydantic import BaseModel

from notionary.blocks.types import BlockType


class ChildPageBlock(BaseModel):
    title: str


class CreateChildPageBlock(BaseModel):
    type: Literal[BlockType.CHILD_PAGE] = BlockType.CHILD_PAGE
    child_page: ChildPageBlock
