from __future__ import annotations
from typing import Any, Optional, Set, Type

from notionary.blocks import NotionBlockElement
from notionary.blocks.shared.models import Block
from notionary.blocks.shared.notion_block_element import BlockContentResult
from notionary.page.markdown_syntax_prompt_generator import (
    MarkdownSyntaxPromptGenerator,
)
from notionary.blocks import TextInlineFormatter

from notionary.blocks import NotionBlockElement
from notionary.telemetry import (
    ProductTelemetry,
    NotionMarkdownSyntaxPromptEvent,
    MarkdownToNotionConversionEvent,
    NotionToMarkdownConversionEvent,
)


class BlockRegistry:
    """Registry of elements that can convert between Markdown and Notion."""

    def __init__(self, elements=None):
        """
        Initialize a new registry instance.

        Args:
            elements: Initial elements to register
        """
        self._elements: list[NotionBlockElement] = []
        self._element_types: Set[Type[NotionBlockElement]] = set()

        if elements:
            for element in elements:
                self.register(element)

        self.telemetry = ProductTelemetry()

    @classmethod
    def create_registry(cls) -> BlockRegistry:
        """
        Create a registry with all standard elements in recommended order.

        """
        from notionary.blocks import BlockRegistryBuilder

        return BlockRegistryBuilder.create_registry()

    def register(self, element_class: Type[NotionBlockElement]) -> bool:
        """
        Register an element class.
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
        Checks if a specific element is contained in the registry.
        """
        return element_class in self._elements

    def find_markdown_handler(self, text: str) -> Optional[Type[NotionBlockElement]]:
        """Find an element that can handle the given markdown text."""
        for element in self._elements:
            if element.match_markdown(text):
                return element
        return None

    def markdown_to_notion(self, text: str) -> BlockContentResult:
        """Convert markdown to Notion block using registered elements."""
        handler = self.find_markdown_handler(text)

        if handler:
            self.telemetry.capture(
                MarkdownToNotionConversionEvent(
                    handler_element_name=handler.__name__,
                )
            )

            return handler.markdown_to_notion(text)
        return None

    def notion_to_markdown(self, block: Block) -> Optional[str]:
        """Convert Notion block to markdown using registered elements."""
        handler = self._find_notion_handler(block)

        if not handler:
            return None

        self.telemetry.capture(
            NotionToMarkdownConversionEvent(
                handler_element_name=handler.__name__,
            )
        )

        return handler.notion_to_markdown(block)

    def get_multiline_elements(self) -> list[Type[NotionBlockElement]]:
        """Get all registered multiline elements."""
        return [element for element in self._elements if element.is_multiline()]

    def get_elements(self) -> list[Type[NotionBlockElement]]:
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

        self.telemetry.capture(NotionMarkdownSyntaxPromptEvent())

        return MarkdownSyntaxPromptGenerator.generate_system_prompt(element_classes)

    def _find_notion_handler(self, block: Block) -> Optional[Type[NotionBlockElement]]:
        """Find an element that can handle the given Notion block."""
        for element in self._elements:
            if element.match_notion(block):
                return element
        return None
