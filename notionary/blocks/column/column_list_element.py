from __future__ import annotations

import re
from typing import Optional

from notionary.blocks.base_block_element import BaseBlockElement
from notionary.blocks.column.column_models import ColumnListBlock, CreateColumnListBlock
from notionary.blocks.markdown_syntax_builder import BlockElementMarkdownInformation
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

    @classmethod
    def get_system_prompt_information(cls) -> Optional[BlockElementMarkdownInformation]:
        """Get system prompt information for column list blocks."""
        return super().get_system_prompt_information(
            description="Column list containers organize multiple columns in side-by-side layouts",
            syntax_examples=[
                "::: columns\n::: column\nContent 1\n:::\n::: column\nContent 2\n:::\n:::"
            ],
            usage_guidelines="Use to create multi-column layouts. Contains individual ::: column blocks. Ends with :::. Each column can have different content and optional width ratios.",
        )
