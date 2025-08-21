from __future__ import annotations

import re

from notionary.blocks.base_block_element import BaseBlockElement
from notionary.blocks.column.column_models import (ColumnListBlock,
                                                   CreateColumnListBlock)
from notionary.blocks.models import Block, BlockCreateResult
from notionary.blocks.types import BlockType


class ColumnListElement(BaseBlockElement):
    """
    Handles the `::: columns` container.
    Individual columns are handled by ColumnElement.
    """

    COLUMNS_START = re.compile(r"^:::\s*columns\s*$")

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        """Check if text starts a columns container."""
        return bool(cls.COLUMNS_START.match(text.strip()))

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        """Check if block is a Notion column_list."""
        return block.type == BlockType.COLUMN_LIST and block.column_list

    @classmethod
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert `::: columns` to Notion ColumnListBlock."""
        if not cls.COLUMNS_START.match(text.strip()):
            return None

        # Empty ColumnListBlock - children (columns) added by stack processor
        column_list_content = ColumnListBlock()
        return CreateColumnListBlock(column_list=column_list_content)
