import re

from notionary.blocks.base_block_element import BaseBlockElement
from notionary.blocks.column.models import ColumnListBlock, CreateColumnListBlock
from notionary.blocks.schemas import Block, BlockCreateResult
from notionary.blocks.syntax_prompt_builder import BlockElementMarkdownInformation
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
    async def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert `::: columns` to Notion ColumnListBlock."""
        if not cls.COLUMNS_START.match(text.strip()):
            return None

        # Empty ColumnListBlock - children (columns) added by stack processor
        column_list_content = ColumnListBlock()
        return CreateColumnListBlock(column_list=column_list_content)

    @classmethod
    @classmethod
    def get_system_prompt_information(cls) -> BlockElementMarkdownInformation | None:
        """Get system prompt information for column list blocks."""
        return BlockElementMarkdownInformation(
            block_type=cls.__name__,
            description="Column list containers organize multiple columns in side-by-side layouts",
            syntax_examples=[
                "::: columns\n::: column\nContent 1\n:::\n::: column\nContent 2\n:::\n:::",
                "::: columns\n::: column 0.6\nMain content\n:::\n::: column 0.4\nSidebar\n:::\n:::",
                "::: columns\n::: column 0.25\nLeft\n:::\n::: column 0.5\nCenter\n:::\n::: column 0.25\nRight\n:::\n:::",
            ],
            usage_guidelines="Use to create multi-column layouts with at least 2 columns. Column width ratios must add up to 1.0 when specified. Each column can contain any block content. Ends with :::.",
        )
