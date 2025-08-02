from typing import Literal
from pydantic import BaseModel

from notionary.blocks.block_models import BlockColor
from notionary.blocks.rich_text.rich_text_models import RichTextObject


class TableBlock(BaseModel):
    table_width: int
    has_column_header: bool = False
    has_row_header: bool = False


class TableRowBlock(BaseModel):
    cells: list[list[RichTextObject]]
    
    
class CreateTableBlock(BaseModel):
    type: Literal["table"] = "table"
    table: TableBlock
    
class CreateTableRowBlock(BaseModel):
    type: Literal["table_row"] = "table_row"
    table_row: TableRowBlock

class TableOfContentsBlock(BaseModel):
    color: BlockColor = "default"


class CreateTableOfContentsBlock(BaseModel):
    type: Literal["table_of_contents"] = "table_of_contents"
    table_of_contents: TableOfContentsBlock
