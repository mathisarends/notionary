from __future__ import annotations
from typing import List, Type
from collections import OrderedDict

from notionary.blocks import (
    ParagraphElement,
    BlockRegistry,
    AudioElement,
    BulletedListElement,
    CalloutElement,
    CodeBlockElement,
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
    def create_full_registry(cls) -> BlockRegistry:
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

    @classmethod
    def create_minimal_registry(cls) -> BlockRegistry:
        """
        Create a minimal registry with just essential text elements.
        Suitable for basic note-taking.
        """
        builder = cls()
        return (
            builder.with_paragraphs()
            .with_headings()
            .with_bulleted_list()
            .with_numbered_list()
        ).build()

    def add_element(
        self, element_class: Type[NotionBlockElement]
    ) -> BlockRegistryBuilder:
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

    def add_elements(
        self, element_classes: List[Type[NotionBlockElement]]
    ) -> BlockRegistryBuilder:
        """
        Add multiple element classes to the registry configuration.

        Args:
            element_classes: List of element classes to add

        Returns:
            Self for method chaining
        """
        for element_class in element_classes:
            self.add_element(element_class)
        return self

    def remove_element(
        self, element_class: Type[NotionBlockElement]
    ) -> BlockRegistryBuilder:
        """
        Remove an element class from the registry configuration.

        Args:
            element_class: The element class to remove

        Returns:
            Self for method chaining
        """
        self._elements.pop(element_class.__name__, None)
        return self

    def move_element_to_end(
        self, element_class: Type[NotionBlockElement]
    ) -> BlockRegistryBuilder:
        """
        Move an existing element to the end of the registry.
        If the element doesn't exist, it will be added.

        Args:
            element_class: The element class to move

        Returns:
            Self for method chaining
        """
        return self.add_element(element_class)

    def _ensure_paragraph_at_end(self) -> None:
        """
        Internal method to ensure ParagraphElement is the last element in the registry.
        """
        if ParagraphElement.__name__ in self._elements:
            paragraph_class = self._elements.pop(ParagraphElement.__name__)
            self._elements[ParagraphElement.__name__] = paragraph_class

    def with_paragraphs(self) -> BlockRegistryBuilder:
        """
        Add support for paragraph elements.
        """
        return self.add_element(ParagraphElement)

    def with_headings(self) -> BlockRegistryBuilder:
        """
        Add support for heading elements.
        """
        return self.add_element(HeadingElement)

    def with_callouts(self) -> BlockRegistryBuilder:
        """
        Add support for callout elements.
        """
        return self.add_element(CalloutElement)

    def with_code(self) -> BlockRegistryBuilder:
        """
        Add support for code blocks.
        """
        return self.add_element(CodeBlockElement)

    def with_dividers(self) -> BlockRegistryBuilder:
        """
        Add support for divider elements.
        """
        return self.add_element(DividerElement)

    def with_tables(self) -> BlockRegistryBuilder:
        """
        Add support for tables.
        """
        return self.add_element(TableElement)

    def with_bulleted_list(self) -> BlockRegistryBuilder:
        """
        Add support for bulleted list elements (unordered lists).
        """
        return self.add_element(BulletedListElement)

    def with_numbered_list(self) -> BlockRegistryBuilder:
        """
        Add support for numbered list elements (ordered lists).
        """
        return self.add_element(NumberedListElement)

    def with_toggles(self) -> BlockRegistryBuilder:
        """
        Add support for toggle elements.
        """
        return self.add_element(ToggleElement)

    def with_quotes(self) -> BlockRegistryBuilder:
        """
        Add support for quote elements.
        """
        return self.add_element(QuoteElement)

    def with_todos(self) -> BlockRegistryBuilder:
        """
        Add support for todo elements.
        """
        return self.add_element(TodoElement)

    def with_bookmarks(self) -> BlockRegistryBuilder:
        """
        Add support for bookmark elements.
        """
        return self.add_element(BookmarkElement)

    def with_images(self) -> BlockRegistryBuilder:
        """
        Add support for image elements.
        """
        return self.add_element(ImageElement)

    def with_videos(self) -> BlockRegistryBuilder:
        """
        Add support for video elements.
        """
        return self.add_element(VideoElement)

    def with_embeds(self) -> BlockRegistryBuilder:
        """
        Add support for embed elements.
        """
        return self.add_element(EmbedElement)

    def with_audio(self) -> BlockRegistryBuilder:
        """
        Add support for audio elements.
        """
        return self.add_element(AudioElement)

    def with_media_support(self) -> BlockRegistryBuilder:
        """
        Add support for media elements (images, videos, audio).
        """
        return self.with_images().with_videos().with_audio()

    def with_mention(self) -> BlockRegistryBuilder:
        return self.add_element(MentionElement)

    def with_toggleable_heading_element(self) -> BlockRegistryBuilder:
        return self.add_element(ToggleableHeadingElement)

    def with_columns(self) -> BlockRegistryBuilder:
        """
        Add support for column elements.
        """
        return self.add_element(ColumnElement)

    def build(self) -> BlockRegistry:
        """
        Build and return the configured BlockRegistry instance.

        This automatically ensures that ParagraphElement is at the end
        of the registry (if present) as a fallback element, unless
        this behavior was explicitly disabled.

        Returns:
            A configured BlockRegistry instance
        """
        if ParagraphElement.__name__ not in self._elements:
            self.add_element(ParagraphElement)
        else:
            self._ensure_paragraph_at_end()

        registry = BlockRegistry()

        # Add elements in the recorded order
        for element_class in self._elements.values():
            registry.register(element_class)

        return registry
