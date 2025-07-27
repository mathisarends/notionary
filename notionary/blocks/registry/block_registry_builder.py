from __future__ import annotations
from typing import Type, TYPE_CHECKING, Self
from collections import OrderedDict

from notionary.blocks import (
    ParagraphElement,
    AudioElement,
    BulletedListElement,
    CalloutElement,
    CodeElement,
    ColumnElement,
    DividerElement,
    EmbedElement,
    HeadingElement,
    ImageElement,
    MentionElement,
    NumberedListElement,
    TableElement,
    TodoElement,
    ToggleElement,
    ToggleableHeadingElement,
    VideoElement,
    BookmarkElement,
    QuoteElement,
    NotionBlockElement,
)

if TYPE_CHECKING:
    from notionary.blocks import BlockRegistry


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
            .with_columns()
            .with_mention()
            .with_paragraphs()
            .with_toggleable_heading_element()
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
        """Add support for paragraph elements."""
        return self._add_element(ParagraphElement)

    def with_headings(self) -> Self:
        """Add support for heading elements."""
        return self._add_element(HeadingElement)

    def with_callouts(self) -> Self:
        """Add support for callout elements."""
        return self._add_element(CalloutElement)

    def with_code(self) -> Self:
        """Add support for code blocks."""
        return self._add_element(CodeElement)

    def with_dividers(self) -> Self:
        """Add support for divider elements."""
        return self._add_element(DividerElement)

    def with_tables(self) -> Self:
        """Add support for tables."""
        return self._add_element(TableElement)

    def with_bulleted_list(self) -> Self:
        """Add support for bulleted list elements (unordered lists)."""
        return self._add_element(BulletedListElement)

    def with_numbered_list(self) -> Self:
        """Add support for numbered list elements (ordered lists)."""
        return self._add_element(NumberedListElement)

    def with_toggles(self) -> Self:
        """Add support for toggle elements."""
        return self._add_element(ToggleElement)

    def with_quotes(self) -> Self:
        """Add support for quote elements."""
        return self._add_element(QuoteElement)

    def with_todos(self) -> Self:
        """Add support for todo elements."""
        return self._add_element(TodoElement)

    def with_bookmarks(self) -> Self:
        """Add support for bookmark elements."""
        return self._add_element(BookmarkElement)

    def with_images(self) -> Self:
        """Add support for image elements."""
        return self._add_element(ImageElement)

    def with_videos(self) -> Self:
        """Add support for video elements."""
        return self._add_element(VideoElement)

    def with_embeds(self) -> Self:
        """Add support for embed elements."""
        return self._add_element(EmbedElement)

    def with_audio(self) -> Self:
        """Add support for audio elements."""
        return self._add_element(AudioElement)

    def with_mention(self) -> Self:
        """Add support for mention elements."""
        return self._add_element(MentionElement)

    def with_toggleable_heading_element(self) -> Self:
        """Add support for toggleable heading elements."""
        return self._add_element(ToggleableHeadingElement)

    def with_columns(self) -> Self:
        """Add support for column elements."""
        return self._add_element(ColumnElement)

    def build(self) -> BlockRegistry:
        """
        Build and return the configured BlockRegistry instance.

        This automatically ensures that ParagraphElement is at the end
        of the registry as a fallback element.

        Returns:
            A configured BlockRegistry instance
        """
        from notionary.blocks import BlockRegistry

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
