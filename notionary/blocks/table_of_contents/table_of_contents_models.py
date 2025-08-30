from typing import Literal, Optional

from pydantic import BaseModel

from notionary.blocks.types import BlockColor


class TableOfContentsBlock(BaseModel):
    """Inneres Payload-Objekt: { table_of_contents: { color: ... } }"""

    color: Optional[BlockColor] = BlockColor.DEFAULT


class CreateTableOfContentsBlock(BaseModel):
    """Create-Payload für den Block: { type: 'table_of_contents', table_of_contents: {...} }"""

    type: Literal["table_of_contents"] = "table_of_contents"
    table_of_contents: TableOfContentsBlock
