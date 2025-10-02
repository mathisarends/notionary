from typing import Literal

from pydantic import BaseModel

from notionary.blocks.types import BlockType


class EquationBlock(BaseModel):
    expression: str


class CreateEquationBlock(BaseModel):
    type: Literal[BlockType.EQUATION] = BlockType.EQUATION
    equation: EquationBlock
