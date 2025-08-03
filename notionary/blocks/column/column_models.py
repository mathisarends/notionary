from __future__ import annotations
from typing import Optional, TYPE_CHECKING

from typing import Literal, Optional
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from notionary.blocks.block_models import BlockCreateRequest


class ColumnBlock(BaseModel):
    column_ratio: Optional[float] = None


class CreateColumnBlock(BaseModel):
    type: Literal["column"] = "column"
    column: ColumnBlock
    children: list[BlockCreateRequest] = Field(default_factory=list)


class ColumnListBlock(BaseModel):
    children: list[CreateColumnBlock] = Field(default_factory=list)


class CreateColumnListBlock(BaseModel):
    type: Literal["column_list"] = "column_list"
    column_list: ColumnListBlock
