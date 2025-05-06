from typing import Dict, Any, Optional, List, Type

from notionary.elements.notion_block_element import NotionBlockElement
from notionary.elements.prompts.synthax_prompt_builder import (
    MarkdownSyntaxPromptBuilder,
)
from notionary.elements.text_inline_formatter import TextInlineFormatter


class BlockElementRegistry:
    """Registry of elements that can convert between Markdown and Notion."""

    def __init__(self, elements=None):
        """
        Initialize a new registry instance.
        """
        self._elements: List[NotionBlockElement] = []

        if elements:
            for element in elements:
                self.register(element)

    def register(self, element_class: Type[NotionBlockElement]):
        """Register an element class."""
        self._elements.append(element_class)
        return self

    def deregister(self, element_class: Type[NotionBlockElement]) -> bool:
        """
        Deregister an element class.
        """
        if element_class in self._elements:
            self._elements.remove(element_class)
            return True
        return False

    def find_markdown_handler(self, text: str) -> Optional[Type[NotionBlockElement]]:
        """Find an element that can handle the given markdown text."""
        for element in self._elements:
            if element.match_markdown(text):
                return element
        return None

    def markdown_to_notion(self, text: str) -> Optional[Dict[str, Any]]:
        """Convert markdown to Notion block using registered elements."""
        handler = self.find_markdown_handler(text)
        if handler:
            return handler.markdown_to_notion(text)
        return None

    def notion_to_markdown(self, block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion block to markdown using registered elements."""
        handler = self._find_notion_handler(block)
        if handler:
            return handler.notion_to_markdown(block)
        return None

    def get_multiline_elements(self) -> List[Type[NotionBlockElement]]:
        """Get all registered multiline elements."""
        return [element for element in self._elements if element.is_multiline()]

    def get_elements(self) -> List[Type[NotionBlockElement]]:
        """Get all registered elements."""
        return self._elements.copy()

    def generate_llm_prompt(self) -> str:
        """
        Generates an LLM system prompt that describes the Markdown syntax of all registered elements.
        """
        element_classes = self._elements.copy()

        formatter_names = [e.__name__ for e in element_classes]
        if "TextInlineFormatter" not in formatter_names:
            element_classes = [TextInlineFormatter] + element_classes

        return MarkdownSyntaxPromptBuilder.generate_system_prompt(element_classes)

    def _find_notion_handler(
        self, block: Dict[str, Any]
    ) -> Optional[Type[NotionBlockElement]]:
        """Find an element that can handle the given Notion block."""
        for element in self._elements:
            if element.match_notion(block):
                return element
        return None
