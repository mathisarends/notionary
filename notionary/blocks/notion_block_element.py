from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from abc import ABC

if TYPE_CHECKING:
    from notionary.blocks.block_models import Block, BlockCreateResult

from notionary.prompts.element_prompt_content import ElementPromptContent


class NotionBlockElement(ABC):
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
    def match_markdown(cls, text: str) -> bool:
        """Check if this element can handle the given markdown text."""
        return bool(cls.markdown_to_notion(text))  # Now calls the class's version

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        """Check if this element can handle the given Notion block."""
        return bool(cls.notion_to_markdown(block))  # Now calls the class's version

    @classmethod
    def is_multiline(cls) -> bool:
        return False

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        """Returns a dictionary with information for LLM prompts about this element."""
