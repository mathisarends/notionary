from __future__ import annotations
from typing import Optional, Type

from notionary.blocks.notion_block_element import NotionBlockElement
from notionary.page.markdown_syntax_prompt_generator import (
    MarkdownSyntaxPromptGenerator,
)
from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter

from notionary.telemetry import (
    ProductTelemetry,
    NotionMarkdownSyntaxPromptEvent,
    MarkdownToNotionConversionEvent,
    NotionToMarkdownConversionEvent,
)

from notionary.blocks.block_models import Block, BlockCreateResult

from notionary.blocks.registry.block_registry_builder import BlockRegistryBuilder


class BlockRegistry:
    """Registry of elements that can convert between Markdown and Notion."""

    def __init__(self, builder: Optional[BlockRegistryBuilder] = None):
        """
        Initialize a new registry instance.

        Args:
            builder: BlockRegistryBuilder instance to delegate operations to
        """
        # Import here to avoid circular imports
        from notionary.blocks.registry.block_registry_builder import (
            BlockRegistryBuilder,
        )

        self._builder: BlockRegistryBuilder = builder or BlockRegistryBuilder()
        self.telemetry = ProductTelemetry()

    @classmethod
    def create_registry(cls) -> BlockRegistry:
        """
        Create a registry with all standard elements in recommended order.
        """
        from notionary.blocks.registry.block_registry_builder import (
            BlockRegistryBuilder,
        )

        builder = BlockRegistryBuilder()
        builder = (
            builder.with_headings()
            .with_callouts()
            .with_code()
            .with_dividers()
            .with_tables()
            .with_bulleted_list()
            .with_numbered_list()
            .with_toggles()
            .with_quotes()
            .with_todos()
            .with_bookmarks()
            .with_images()
            .with_videos()
            .with_embeds()
            .with_audio()
            .with_paragraphs()
            .with_toggleable_heading_element()
            .with_columns()
            .with_equation()
            .with_table_of_contents()
            .with_breadcrumbs()
        )

        return cls(builder=builder)

    @property
    def builder(self) -> BlockRegistryBuilder:
        return self._builder

    def register(self, element_class: Type[NotionBlockElement]) -> bool:
        """
        Register an element class via builder.
        """
        initial_count = len(self._builder._elements)
        self._builder._add_element(element_class)
        return len(self._builder._elements) > initial_count

    def deregister(self, element_class: Type[NotionBlockElement]) -> bool:
        """
        Deregister an element class via builder.
        """
        initial_count = len(self._builder._elements)
        self._builder.remove_element(element_class)
        return len(self._builder._elements) < initial_count

    def contains(self, element_class: Type[NotionBlockElement]) -> bool:
        """
        Checks if a specific element is contained in the registry.
        """
        return element_class.__name__ in self._builder._elements

    def find_markdown_handler(self, text: str) -> Optional[Type[NotionBlockElement]]:
        """Find an element that can handle the given markdown text."""
        for element in self._builder._elements.values():
            if element.match_markdown(text):
                return element
        return None

    def markdown_to_notion(self, text: str) -> "BlockCreateResult":
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

    def notion_to_markdown(self, block: "Block") -> Optional[str]:
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

    def get_elements(self) -> list[Type[NotionBlockElement]]:
        """Get all registered elements."""
        return list(self._builder._elements.values())

    def get_notion_markdown_syntax_prompt(self) -> str:
        """
        Generates an LLM system prompt that describes the Markdown syntax of all registered elements.
        """
        element_classes = list(self._builder._elements.values())

        formatter_names = [e.__name__ for e in element_classes]
        if "TextInlineFormatter" not in formatter_names:
            element_classes = element_classes + [TextInlineFormatter]

        self.telemetry.capture(NotionMarkdownSyntaxPromptEvent())

        return MarkdownSyntaxPromptGenerator.generate_system_prompt(element_classes)

    def _find_notion_handler(self, block: Block) -> Optional[Type[NotionBlockElement]]:
        """Find an element that can handle the given Notion block."""
        for element in self._builder._elements.values():
            if element.match_notion(block):
                return element
        return None
