from typing import Literal

from pydantic import BaseModel


class EquationBlock(BaseModel):
    expression: str


class CreateEquationBlock(BaseModel):
    type: Literal["equation"] = "equation"
    equation: EquationBlock
