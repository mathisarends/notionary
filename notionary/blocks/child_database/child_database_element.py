from __future__ import annotations

import re
from typing import Optional, TYPE_CHECKING

from notionary.blocks.base_block_element import BaseBlockElement
from notionary.blocks.syntax_prompt_builder import BlockElementMarkdownInformation
from notionary.blocks.models import Block, BlockType

if TYPE_CHECKING:
    from notionary.page.writer.markdown_to_notion_converter_context import (
        ConverterContext,
    )


class ChildDatabaseElement(BaseBlockElement):
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
        cls, text: str, context: Optional[ConverterContext] = None
    ) -> Optional[str]:
        """
        Convert markdown database syntax to actual Notion database.
        Returns the database_id if successful, None otherwise.
        """
        if context is None:
            raise ValueError("ConversionContext required for child_database creation")

        text = text.strip()

        # Try bracket pattern first
        match = cls.PATTERN_BRACKET.match(text)
        if not match:
            # Try emoji pattern
            match = cls.PATTERN_EMOJI.match(text)

        if not match:
            return None

        title = match.group(1).strip()
        if not title:
            return None

        # Reject multiline titles
        if "\n" in title or "\r" in title:
            return None

        try:
            database_client = context.require_database_client()
            parent_page_id = context.require_page_id()

            # Create the actual database
            database_response = await database_client.create_database(
                title=title, parent_page_id=parent_page_id
            )
            return database_response.id

        except Exception as e:
            # Log error or handle appropriately
            print(f"Failed to create database '{title}': {e}")
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
