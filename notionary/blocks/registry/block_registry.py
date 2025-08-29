from __future__ import annotations

from typing import Optional, Type

from notionary.blocks.base_block_element import BaseBlockElement
from notionary.blocks.registry.block_registry_builder import BlockRegistryBuilder
from notionary.telemetry import (
    ProductTelemetry,
)


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
            .with_toggleable_heading_element()
            .with_quotes()
            .with_todos()
            .with_bookmarks()
            .with_images()
            .with_videos()
            .with_embeds()
            .with_audio()
            .with_columns()
            .with_equation()
            .with_table_of_contents()
            .with_breadcrumbs()
            .with_child_database()
            .with_file()
            .with_paragraphs()  # position here is important - its a fallback!
        )

        return cls(builder=builder)

    @property
    def builder(self) -> BlockRegistryBuilder:
        return self._builder

    def register(self, element_class: Type[BaseBlockElement]) -> bool:
        """
        Register an element class via builder.
        """
        initial_count = len(self._builder._elements)
        self._builder._add_element(element_class)
        return len(self._builder._elements) > initial_count

    def deregister(self, element_class: Type[BaseBlockElement]) -> bool:
        """
        Deregister an element class via builder.
        """
        initial_count = len(self._builder._elements)
        self._builder.remove_element(element_class)
        return len(self._builder._elements) < initial_count

    def contains(self, element_class: Type[BaseBlockElement]) -> bool:
        """
        Checks if a specific element is contained in the registry.
        """
        return element_class.__name__ in self._builder._elements

    def get_elements(self) -> list[Type[BaseBlockElement]]:
        """Get all registered elements."""
        return list(self._builder._elements.values())
