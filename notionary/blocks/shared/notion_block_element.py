from typing import Optional, Any, TypeAlias, Union
from abc import ABC

from notionary.blocks.prompts.element_prompt_content import ElementPromptContent

NotionBlock: TypeAlias = dict[str, Any]
NotionBlockResult: TypeAlias = Optional[Union[list[dict[str, Any]], dict[str, Any]]]


class NotionBlockElement(ABC):
    """Base class for elements that can be converted between Markdown and Notion."""

    @classmethod
    def markdown_to_notion(cls, text: str) -> NotionBlockResult:
        """Convert markdown to Notion blocks (can return multiple blocks or single block)."""

    @classmethod
    def notion_to_markdown(cls, block: dict[str, any]) -> Optional[str]:
        """Convert Notion block to markdown."""

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        """Check if this element can handle the given markdown text."""
        return bool(cls.markdown_to_notion(text))  # Now calls the class's version

    @classmethod
    def match_notion(cls, block: dict[str, any]) -> bool:
        """Check if this element can handle the given Notion block."""
        return bool(cls.notion_to_markdown(block))  # Now calls the class's version

    @classmethod
    def is_multiline(cls) -> bool:
        return False

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        """Returns a dictionary with information for LLM prompts about this element."""
