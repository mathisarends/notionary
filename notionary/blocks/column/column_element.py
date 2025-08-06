from __future__ import annotations
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from notionary.blocks.block_models import Block, BlockCreateResult

from notionary.blocks.block_models import Block
from notionary.blocks.column.column_models import ColumnBlock, CreateColumnBlock
from notionary.blocks.notion_block_element import NotionBlockElement
from notionary.prompts import ElementPromptBuilder, ElementPromptContent


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
        return block.type == "column"

    @classmethod
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert `::: column` to Notion ColumnBlock."""
        if not cls.COLUMN_START.match(text.strip()):
            return None

        # Empty ColumnBlock - content added by stack processor
        column_content = ColumnBlock(column_ratio=None)
        return CreateColumnBlock(column=column_content)

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        """LLM prompt for individual column."""
        return (
            ElementPromptBuilder()
            .with_description("Creates a single column within a column layout.")
            .with_syntax("::: column\n[content]\n:::")
            .with_examples.build()
        )
