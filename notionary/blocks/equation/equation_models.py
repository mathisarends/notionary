from pydantic import BaseModel
from typing_extensions import Literal


class EquationBlock(BaseModel):
    expression: str


class CreateEquationBlock(BaseModel):
    type: Literal["equation"] = "equation"
    equation: EquationBlock
