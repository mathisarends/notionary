from __future__ import annotations

from abc import ABC
from typing import Optional

from notionary.blocks.markdown_syntax_builder import BlockElementMarkdownInformation
from notionary.blocks.models import Block, BlockCreateResult


class BaseBlockElement(ABC):
    """Base class for elements that can be converted between Markdown and Notion."""

    @classmethod
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """
        Convert markdown to Notion block content.

        Returns:
            - BlockContent: Single block content (e.g., ToDoBlock, ParagraphBlock)
            - list[BlockContent]: Multiple block contents
            - None: Cannot convert this markdown
        """

    @classmethod
    def notion_to_markdown(cls, block: Block) -> Optional[str]:
        """Convert Notion block to markdown."""

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        """Check if this element can handle the given Notion block."""
        return bool(cls.notion_to_markdown(block))  # Now calls the class's version

    @classmethod
    def get_system_prompt_information(
        cls, description: str, syntax_examples: list[str], usage_guidelines: str
    ) -> Optional[BlockElementMarkdownInformation]:
        return BlockElementMarkdownInformation(
            block_type=cls.__name__,
            description=description,
            syntax_examples=syntax_examples,
            usage_guidelines=usage_guidelines,
        )
