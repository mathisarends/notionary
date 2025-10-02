from typing import Literal

from pydantic import BaseModel

from notionary.blocks.types import BlockColor, BlockType


class TableOfContentsBlock(BaseModel):
    """Inneres Payload-Objekt: { table_of_contents: { color: ... } }"""

    color: BlockColor | None = BlockColor.DEFAULT


class CreateTableOfContentsBlock(BaseModel):
    """Create-Payload für den Block: { type: 'table_of_contents', table_of_contents: {...} }"""

    type: Literal[BlockType.TABLE_OF_CONTENTS] = BlockType.TABLE_OF_CONTENTS
    table_of_contents: TableOfContentsBlock
