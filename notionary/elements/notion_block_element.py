from functools import wraps
from typing import Dict, Any, Optional
from abc import ABC

from notionary.prompting.element_prompt_content import ElementPromptContent


class NotionBlockElement(ABC):
    """Base class for elements that can be converted between Markdown and Notion."""

    @classmethod
    def markdown_to_notion(cls, text: str) -> Optional[Dict[str, Any]]:
        """Convert markdown to Notion block."""

    @classmethod
    def notion_to_markdown(cls, block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion block to markdown."""

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        """Check if this element can handle the given markdown text."""
        return bool(cls.markdown_to_notion(text))  # Now calls the class's version

    @classmethod
    def match_notion(cls, block: Dict[str, Any]) -> bool:
        """Check if this element can handle the given Notion block."""
        return bool(cls.notion_to_markdown(block))  # Now calls the class's version

    @classmethod
    def is_multiline(cls) -> bool:
        return False

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        """Returns a dictionary with information for LLM prompts about this element."""
