from typing import Literal, Optional

from pydantic import BaseModel


class ColumnBlock(BaseModel):
    width_ratio: Optional[float] = None


class CreateColumnBlock(BaseModel):
    type: Literal["column"] = "column"
    column: ColumnBlock


class ColumnListBlock(BaseModel):
    pass


class CreateColumnListBlock(BaseModel):
    type: Literal["column_list"] = "column_list"
    column_list: ColumnListBlock
