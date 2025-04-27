import inspect
from typing import Dict, Any, Optional
from abc import ABC

from notionary.elements.prompts.element_prompt_content import ElementPromptContent


class NotionBlockElement(ABC):
    """Base class for elements that can be converted between Markdown and Notion."""

    @staticmethod
    def markdown_to_notion(text: str) -> Optional[Dict[str, Any]]:
        """Convert markdown to Notion block."""

    @staticmethod
    def notion_to_markdown(block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion block to markdown."""

    @staticmethod
    def match_markdown(text: str) -> bool:
        """Check if this element can handle the given markdown text."""
        return bool(NotionBlockElement.markdown_to_notion(text))

    @staticmethod
    def match_notion(block: Dict[str, Any]) -> bool:
        """Check if this element can handle the given Notion block."""
        return bool(NotionBlockElement.notion_to_markdown(block))

    @staticmethod
    def is_multiline() -> bool:
        return False

    @classmethod
    def get_llm_documentation(cls) -> str:
        """
        Returns documentation specifically formatted for LLM system prompts.
        Can be overridden by subclasses to provide custom LLM-friendly documentation.

        By default, returns the class docstring.
        """

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        """
        Returns a dictionary with information for LLM prompts about this element.
        This default implementation extracts information from the class docstring.
        Subclasses should override this method to provide more structured information.

        Returns:
            Dictionary with documentation information
        """
        return {"description": inspect.cleandoc(cls.__doc__ or ""), "examples": []}
