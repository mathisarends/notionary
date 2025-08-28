from __future__ import annotations

import re
from typing import Optional

from notionary.blocks.base_block_element import BaseBlockElement
from notionary.blocks.syntax_prompt_builder import BlockElementMarkdownInformation
from notionary.blocks.models import Block, BlockType
from notionary.util import LoggingMixin

class ChildDatabaseElement(BaseBlockElement, LoggingMixin):
    """
    Handles conversion between Markdown database references and Notion child database blocks.

    Creates new databases when converting from markdown.
    """

    PATTERN_BRACKET = re.compile(r"^\[database:\s*(.+)\]$", re.IGNORECASE)
    PATTERN_EMOJI = re.compile(r"^📊\s*(.+)$")

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return block.type == BlockType.CHILD_DATABASE and block.child_database

    @classmethod
    async def markdown_to_notion(
        cls, text: str
    ) -> Optional[str]:
        """
        Convert markdown database syntax to actual Notion database.
        Returns the database_id if successful, None otherwise.
        """
        cls.logger.warning("Creating database from markdown is not supported via the block api. Call the create_child_page method in NotionPage instead.s")
        return None

    @classmethod
    async def notion_to_markdown(cls, block: Block) -> Optional[str]:
        if block.type != BlockType.CHILD_DATABASE or not block.child_database:
            return None

        title = block.child_database.title
        if not title or not title.strip():
            return None

        # Use bracket syntax for output
        return f"[database: {title.strip()}]"

    @classmethod
    def get_system_prompt_information(cls) -> Optional[BlockElementMarkdownInformation]:
        """Get system prompt information for child database blocks."""
        return BlockElementMarkdownInformation(
            block_type=cls.__name__,
            description="Creates new embedded databases within a Notion page",
            syntax_examples=[
                "[database: Project Tasks]",
                "[database: Customer Information]",
                "📊 Sales Pipeline",
                "📊 Team Directory",
            ],
            usage_guidelines="Use to create new databases that will be embedded in the page. The database will be created with a basic 'Name' property and can be customized later.",
        )
