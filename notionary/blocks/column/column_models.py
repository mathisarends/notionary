from typing import Literal

from pydantic import BaseModel, Field

from notionary.blocks.models import BlockCreateRequest
from notionary.blocks.types import BlockType


class ColumnBlock(BaseModel):
    width_ratio: float | None = None
    children: list[BlockCreateRequest] = Field(default_factory=list)


class CreateColumnBlock(BaseModel):
    type: Literal[BlockType.COLUMN] = BlockType.COLUMN
    column: ColumnBlock


class ColumnListBlock(BaseModel):
    children: list[CreateColumnBlock] = Field(default_factory=list)


class CreateColumnListBlock(BaseModel):
    type: Literal[BlockType.COLUMN_LIST] = BlockType.COLUMN_LIST
    column_list: ColumnListBlock
