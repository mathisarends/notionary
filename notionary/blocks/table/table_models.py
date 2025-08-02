from typing import Literal
from pydantic import BaseModel

from notionary.blocks.block_models import BlockColor, RichTextObject


class TableBlock(BaseModel):
    table_width: int
    has_column_header: bool = False
    has_row_header: bool = False


class TableRowBlock(BaseModel):
    cells: list[list[RichTextObject]]


class TableOfContentsBlock(BaseModel):
    color: BlockColor = "default"


class CreateTableOfContentsBlock(BaseModel):
    type: Literal["table_of_contents"] = "table_of_contents"
    table_of_contents: TableOfContentsBlock
