from __future__ import annotations
from typing import Dict, Any, Optional, List, Set, Type

from notionary.blocks.notion_block_element import NotionBlockElement
from notionary.prompting.markdown_syntax_prompt_generator import (
    MarkdownSyntaxPromptGenerator,
)
from notionary.blocks.text_inline_formatter import TextInlineFormatter

from notionary.blocks.notion_block_element import NotionBlockElement


class BlockRegistry:
    """Registry of elements that can convert between Markdown and Notion."""

    def __init__(self, elements=None):
        """
        Initialize a new registry instance.

        Args:
            elements: Initial elements to register
            builder: The builder that created this registry (optional)
        """
        self._elements: List[NotionBlockElement] = []
        self._element_types: Set[Type[NotionBlockElement]] = set()

        if elements:
            for element in elements:
                self.register(element)

    def to_builder(self):
        """
        Convert this registry to a builder for modifications.
        Imports only when needed to avoid circular imports.
        """
        from notionary.blocks import (
            BlockRegistryBuilder,
        )

        builder = BlockRegistryBuilder()
        for element in self._elements:
            builder.add_element(element)
        return builder

    @property
    def builder(self):
        """
        Returns a new builder pre-configured with the current registry elements.
        Uses lazy import to avoid circular dependencies.
        """
        return self.to_builder()

    def register(self, element_class: Type[NotionBlockElement]) -> bool:
        """
        Register an element class.

        Args:
            element_class: The element class to register

        Returns:
            bool: True if element was added, False if it already existed
        """
        if element_class in self._element_types:
            return False

        self._elements.append(element_class)
        self._element_types.add(element_class)
        return True

    def deregister(self, element_class: Type[NotionBlockElement]) -> bool:
        """
        Deregister an element class.
        """
        if element_class in self._element_types:
            self._elements.remove(element_class)
            self._element_types.remove(element_class)
            return True
        return False

    def contains(self, element_class: Type[NotionBlockElement]) -> bool:
        """
        Prüft, ob ein bestimmtes Element im Registry enthalten ist.

        Args:
            element_class: Die zu prüfende Element-Klasse

        Returns:
            bool: True, wenn das Element enthalten ist, sonst False
        """
        return element_class in self._elements

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

    def get_notion_markdown_syntax_prompt(self) -> str:
        """
        Generates an LLM system prompt that describes the Markdown syntax of all registered elements.
        """
        element_classes = self._elements.copy()

        formatter_names = [e.__name__ for e in element_classes]
        if "TextInlineFormatter" not in formatter_names:
            element_classes = element_classes + [TextInlineFormatter]

        return MarkdownSyntaxPromptGenerator.generate_system_prompt(element_classes)

    def _find_notion_handler(
        self, block: Dict[str, Any]
    ) -> Optional[Type[NotionBlockElement]]:
        """Find an element that can handle the given Notion block."""
        for element in self._elements:
            if element.match_notion(block):
                return element
        return None
