from __future__ import annotations

from collections import OrderedDict
from typing import TYPE_CHECKING, Self, Type

from notionary.blocks.audio import AudioElement
from notionary.blocks.base_block_element import BaseBlockElement
from notionary.blocks.bookmark import BookmarkElement
from notionary.blocks.breadcrumbs import BreadcrumbElement
from notionary.blocks.bulleted_list import BulletedListElement
from notionary.blocks.callout import CalloutElement
from notionary.blocks.code import CodeElement
from notionary.blocks.column import ColumnElement, ColumnListElement
from notionary.blocks.divider import DividerElement
from notionary.blocks.embed import EmbedElement
from notionary.blocks.equation import EquationElement
from notionary.blocks.heading import HeadingElement
from notionary.blocks.image_block import ImageElement
from notionary.blocks.numbered_list import NumberedListElement
from notionary.blocks.paragraph import ParagraphElement
from notionary.blocks.quote import QuoteElement
from notionary.blocks.table import TableElement
from notionary.blocks.table_of_contents import TableOfContentsElement
from notionary.blocks.todo import TodoElement
from notionary.blocks.toggle import ToggleElement
from notionary.blocks.toggleable_heading import ToggleableHeadingElement
from notionary.blocks.video import VideoElement

if TYPE_CHECKING:
    from notionary.blocks.registry.block_registry import BlockRegistry


class BlockRegistryBuilder:
    """
    True builder for constructing BlockRegistry instances.

    This builder allows for incremental construction of registry instances
    with specific configurations of block elements.
    """

    def __init__(self):
        """Initialize a new builder with an empty element list."""
        self._elements = OrderedDict()

    @classmethod
    def create_registry(cls) -> BlockRegistry:
        """
        Start with all standard elements in recommended order.
        """
        builder = cls()
        return (
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
        ).build()

    def remove_element(self, element_class: Type[BaseBlockElement]) -> Self:
        """
        Remove an element class from the registry configuration.

        Args:
            element_class: The element class to remove

        Returns:
            Self for method chaining
        """
        self._elements.pop(element_class.__name__, None)
        return self

    # WITH methods (existing)
    def with_paragraphs(self) -> Self:
        return self._add_element(ParagraphElement)

    def with_headings(self) -> Self:
        return self._add_element(HeadingElement)

    def with_callouts(self) -> Self:
        return self._add_element(CalloutElement)

    def with_code(self) -> Self:
        return self._add_element(CodeElement)

    def with_dividers(self) -> Self:
        return self._add_element(DividerElement)

    def with_tables(self) -> Self:
        return self._add_element(TableElement)

    def with_bulleted_list(self) -> Self:
        return self._add_element(BulletedListElement)

    def with_numbered_list(self) -> Self:
        return self._add_element(NumberedListElement)

    def with_toggles(self) -> Self:
        return self._add_element(ToggleElement)

    def with_quotes(self) -> Self:
        return self._add_element(QuoteElement)

    def with_todos(self) -> Self:
        return self._add_element(TodoElement)

    def with_bookmarks(self) -> Self:
        return self._add_element(BookmarkElement)

    def with_images(self) -> Self:
        return self._add_element(ImageElement)

    def with_videos(self) -> Self:
        return self._add_element(VideoElement)

    def with_embeds(self) -> Self:
        return self._add_element(EmbedElement)

    def with_audio(self) -> Self:
        return self._add_element(AudioElement)

    def with_toggleable_heading_element(self) -> Self:
        return self._add_element(ToggleableHeadingElement)

    def with_columns(self) -> Self:
        self._add_element(ColumnListElement)
        self._add_element(ColumnElement)
        return self

    def with_equation(self) -> Self:
        return self._add_element(EquationElement)

    def with_table_of_contents(self) -> Self:
        return self._add_element(TableOfContentsElement)

    def with_breadcrumbs(self) -> Self:
        return self._add_element(BreadcrumbElement)

    def without_headings(self) -> Self:
        return self.remove_element(HeadingElement)

    def without_callouts(self) -> Self:
        return self.remove_element(CalloutElement)

    def without_code(self) -> Self:
        return self.remove_element(CodeElement)

    def without_dividers(self) -> Self:
        return self.remove_element(DividerElement)

    def without_tables(self) -> Self:
        return self.remove_element(TableElement)

    def without_bulleted_list(self) -> Self:
        return self.remove_element(BulletedListElement)

    def without_numbered_list(self) -> Self:
        return self.remove_element(NumberedListElement)

    def without_toggles(self) -> Self:
        return self.remove_element(ToggleElement)

    def without_quotes(self) -> Self:
        return self.remove_element(QuoteElement)

    def without_todos(self) -> Self:
        return self.remove_element(TodoElement)

    def without_bookmarks(self) -> Self:
        return self.remove_element(BookmarkElement)

    def without_images(self) -> Self:
        return self.remove_element(ImageElement)

    def without_videos(self) -> Self:
        return self.remove_element(VideoElement)

    def without_embeds(self) -> Self:
        return self.remove_element(EmbedElement)

    def without_audio(self) -> Self:
        return self.remove_element(AudioElement)

    def without_toggleable_heading_element(self) -> Self:
        return self.remove_element(ToggleableHeadingElement)

    def without_columns(self) -> Self:
        self.remove_element(ColumnListElement)
        self.remove_element(ColumnElement)
        return self

    def without_equation(self) -> Self:
        return self.remove_element(EquationElement)

    def without_table_of_contents(self) -> Self:
        return self.remove_element(TableOfContentsElement)

    def without_breadcrumbs(self) -> Self:
        return self.remove_element(BreadcrumbElement)

    def build(self) -> BlockRegistry:
        """
        Build and return the configured BlockRegistry instance.
        """
        from notionary.blocks.registry.block_registry import BlockRegistry

        # Ensure ParagraphElement is always present and at the end
        self._ensure_paragraph_at_end()

        registry = BlockRegistry()

        # Add elements in the recorded order
        for element_class in self._elements.values():
            registry.register(element_class)

        return registry

    def _ensure_paragraph_at_end(self) -> None:
        """
        Internal method to ensure ParagraphElement is the last element in the registry.
        If ParagraphElement is not present, it will be added.
        """
        # Remove if present, then always add at the end
        self._elements.pop(ParagraphElement.__name__, None)
        self._elements[ParagraphElement.__name__] = ParagraphElement

    def _add_element(self, element_class: Type[BaseBlockElement]) -> Self:
        """
        Add an element class to the registry configuration.
        If the element already exists, it's moved to the end.

        Args:
            element_class: The element class to add

        Returns:
            Self for method chaining
        """
        self._elements.pop(element_class.__name__, None)
        self._elements[element_class.__name__] = element_class

        return self
