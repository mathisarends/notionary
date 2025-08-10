from __future__ import annotations
import re

from notionary.blocks.block_models import Block, BlockCreateResult

from notionary.blocks.block_models import Block, BlockType
from notionary.blocks.column.column_models import ColumnBlock, CreateColumnBlock
from notionary.blocks.notion_block_element import NotionBlockElement



class ColumnElement(NotionBlockElement):
    """
    Handles individual `::: column` blocks.
    Content is automatically added by the stack processor.
    """

    COLUMN_START = re.compile(r"^:::\s*column\s*$")

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        """Check if text starts a single column."""
        return bool(cls.COLUMN_START.match(text.strip()))

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        """Check if block is a Notion column."""
        return block.type == BlockType.COLUMN and block.column

    @classmethod
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert `::: column` to Notion ColumnBlock."""
        if not cls.COLUMN_START.match(text.strip()):
            return None

        # Empty ColumnBlock - content added by stack processor
        column_content = ColumnBlock(column_ratio=None)
        return CreateColumnBlock(column=column_content)