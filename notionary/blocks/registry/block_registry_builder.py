from __future__ import annotations
from typing import Type, TYPE_CHECKING, Self
from collections import OrderedDict

from notionary.blocks.audio.audio_element import AudioElement
from notionary.blocks.bookmark.bookmark_element import BookmarkElement
from notionary.blocks.bulleted_list.bulleted_list_element import BulletedListElement
from notionary.blocks.callout.callout_element import CalloutElement
from notionary.blocks.code.code_element import CodeElement
from notionary.blocks.column.column_element import ColumnElement
from notionary.blocks.column.column_list_element import ColumnListElement
from notionary.blocks.divider.divider_element import DividerElement
from notionary.blocks.embed.embed_element import EmbedElement
from notionary.blocks.equation.equation_element import EquationElement
from notionary.blocks.heading.heading_element import HeadingElement
from notionary.blocks.ignore_element.IgnoreElement import IgnoreElement
from notionary.blocks.image_block.image_element import ImageElement
from notionary.blocks.notion_block_element import NotionBlockElement
from notionary.blocks.numbered_list.numbered_list_element import NumberedListElement
from notionary.blocks.paragraph.paragraph_element import ParagraphElement
from notionary.blocks.quote.quote_element import QuoteElement
from notionary.blocks.table.table_element import TableElement
from notionary.blocks.table_of_contents.table_of_contents_element import (
    TableOfContentsElement,
)
from notionary.blocks.breadcrumbs.breadcrumb_element import BreadcrumbElement
from notionary.blocks.todo.todo_element import TodoElement
from notionary.blocks.toggle.toggle_element import ToggleElement
from notionary.blocks.toggleable_heading.toggleable_heading_element import (
    ToggleableHeadingElement,
)
from notionary.blocks.video.video_element import VideoElement

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
            .with_ignore_element()
            .with_breadcrumbs()
        ).build()

    def remove_element(self, element_class: Type[NotionBlockElement]) -> Self:
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

    def with_ignore_element(self) -> Self:
        return self._add_element(IgnoreElement)

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

    def _add_element(self, element_class: Type[NotionBlockElement]) -> Self:
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
