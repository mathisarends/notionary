from __future__ import annotations

import re

from notionary.blocks.mappings.base import BaseBlockElement
from notionary.blocks.schemas import Block, BlockCreateResult, BlockType
from notionary.blocks.syntax_prompt_builder import BlockElementMarkdownInformation
from notionary.page.page_context import get_page_context


class ChildPageElement(BaseBlockElement):
    """
    Handles conversion between Markdown page references and Notion child page blocks.

    Creates new pages when converting from markdown.
    """

    PATTERN_BRACKET = re.compile(r"^\[page:\s*(.+)\]$", re.IGNORECASE)
    PATTERN_EMOJI = re.compile(r"^[📝📄]\s*(.+)$")

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return block.type == BlockType.CHILD_PAGE and getattr(block, "child_page", None)

    @classmethod
    async def markdown_to_notion(cls, text: str) -> BlockCreateResult | None:
        """
        Convert markdown page syntax to an actual Notion page.
        Returns None since child_page blocks are created implicitly via Pages API (not Blocks API).
        """
        context = get_page_context()

        text = text.strip()

        match = cls.PATTERN_BRACKET.match(text)
        if not match:
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
            # Create the actual page using context
            await context.page_client.create_page(
                title=title,
                parent_page_id=context.page_id,
            )
            # Return None as per BaseBlockElement convention:
            # child_page blocks cannot be written through the Blocks API directly.
            # Creating a page under the parent page will automatically insert a child_page block.
            return None

        except Exception as e:
            print(f"Failed to create page '{title}': {e}")
            return None

    @classmethod
    async def notion_to_markdown(cls, block: Block) -> str | None:
        if block.type != BlockType.CHILD_PAGE or not getattr(block, "child_page", None):
            return None

        title = block.child_page.title
        if not title or not title.strip():
            return None

        # Use bracket syntax for output
        return f"[page: {title.strip()}]"

    @classmethod
    def get_system_prompt_information(cls) -> BlockElementMarkdownInformation | None:
        """Get system prompt information for child page blocks."""
        return BlockElementMarkdownInformation(
            block_type=cls.__name__,
            description="Creates new sub-pages within a Notion page.",
            syntax_examples=[
                "[page: Meeting Notes]",
                "[page: Ideas]",
                "📝 Project Overview",
                "📄 Research Log",
            ],
            usage_guidelines=(
                "Use to create new pages that will appear as child_page blocks in the current page. "
                "Pages are created via the Pages API with the current page as parent."
            ),
        )
