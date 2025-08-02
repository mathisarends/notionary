from typing import Literal
from pydantic import BaseModel


class DividerBlock(BaseModel):
    pass


class CreateDividerBlock(BaseModel):
    type: Literal["divider"] = "divider"
    divider: DividerBlock
