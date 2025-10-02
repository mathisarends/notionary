from typing import Literal

from pydantic import BaseModel

from notionary.blocks.types import BlockType


class ChildDatabaseBlock(BaseModel):
    title: str


class CreateChildDatabaseBlock(BaseModel):
    type: Literal[BlockType.CHILD_DATABASE] = BlockType.CHILD_DATABASE
    child_database: ChildDatabaseBlock
