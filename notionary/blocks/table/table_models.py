from typing import Literal

from pydantic import BaseModel

from notionary.blocks.rich_text.rich_text_models import RichText
from notionary.blocks.types import BlockType


class TableRowBlock(BaseModel):
    cells: list[list[RichText]]


class CreateTableRowBlock(BaseModel):
    type: Literal[BlockType.TABLE_ROW] = BlockType.TABLE_ROW
    table_row: TableRowBlock


class TableBlock(BaseModel):
    table_width: int
    has_column_header: bool = False
    has_row_header: bool = False
    children: list[CreateTableRowBlock] = []


class CreateTableBlock(BaseModel):
    type: Literal[BlockType.TABLE] = BlockType.TABLE
    table: TableBlock
