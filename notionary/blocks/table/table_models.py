from __future__ import annotations
from typing import Literal
from pydantic import BaseModel

from notionary.blocks.block_models import BlockColor
from notionary.blocks.rich_text.rich_text_models import RichTextObject


class TableBlock(BaseModel):
    table_width: int
    has_column_header: bool = False
    has_row_header: bool = False
    children: list[CreateTableRowBlock] = [] 


class TableRowBlock(BaseModel):
    cells: list[list[RichTextObject]]


class CreateTableRowBlock(BaseModel):
    type: Literal["table_row"] = "table_row"
    table_row: TableRowBlock


class CreateTableBlock(BaseModel):
    type: Literal["table"] = "table"
    table: TableBlock