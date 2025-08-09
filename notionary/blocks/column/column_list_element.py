from __future__ import annotations

import re
from notionary.blocks.block_models import Block, BlockCreateResult

from notionary.blocks.block_models import Block
from notionary.blocks.column.column_models import ColumnListBlock, CreateColumnListBlock
from notionary.blocks.notion_block_element import NotionBlockElement
from notionary.prompts import ElementPromptBuilder, ElementPromptContent


class ColumnListElement(NotionBlockElement):
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
        return block.type == "column_list"

    @classmethod
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert `::: columns` to Notion ColumnListBlock."""
        if not cls.COLUMNS_START.match(text.strip()):
            return None

        # Empty ColumnListBlock - children (columns) added by stack processor
        column_list_content = ColumnListBlock()
        return CreateColumnListBlock(column_list=column_list_content)

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        """LLM prompt for column container."""
        return (
            ElementPromptBuilder()
            .with_description("Creates a multi-column layout container.")
            .with_syntax("::: columns\n[column content]\n:::")
            .build()
        )
