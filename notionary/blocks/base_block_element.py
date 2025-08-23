from __future__ import annotations

from abc import ABC
from typing import Optional

from notionary.blocks.syntax_prompt_builder import BlockElementMarkdownInformation
from notionary.blocks.models import Block, BlockCreateResult


class BaseBlockElement(ABC):
    """Base class for elements that can be converted between Markdown and Notion."""

    @classmethod
    async def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """
        Convert markdown to Notion block content.

        Returns:
            - BlockContent: Single block content (e.g., ToDoBlock, ParagraphBlock)
            - list[BlockContent]: Multiple block contents
            - None: Cannot convert this markdown
        """

    @classmethod
    async def notion_to_markdown(cls, block: Block) -> Optional[str]:
        """Convert Notion block to markdown."""

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        """Check if this element can handle the given Notion block."""
        # Default implementation - subclasses should override this method
        # Cannot call async notion_to_markdown here
        return False

    @classmethod
    def get_system_prompt_information(cls) -> Optional[BlockElementMarkdownInformation]:
        """Get system prompt information for this block element.

        Subclasses should override this method to provide their specific information.
        Return None if the element should not be included in documentation.
        """
        return None
