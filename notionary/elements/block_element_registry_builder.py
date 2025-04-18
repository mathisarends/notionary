from __future__ import annotations
from typing import List, Type
from collections import OrderedDict

from notionary.elements.audio_element import AudioElement
from notionary.elements.embed_element import EmbedElement
from notionary.elements.mention_element import MentionElement
from notionary.elements.notion_block_element import NotionBlockElement
from notionary.elements.block_element_registry import (
    BlockElementRegistry,
)

from notionary.elements.paragraph_element import ParagraphElement
from notionary.elements.heading_element import HeadingElement
from notionary.elements.callout_element import CalloutElement
from notionary.elements.code_block_element import CodeBlockElement
from notionary.elements.divider_element import DividerElement
from notionary.elements.table_element import TableElement
from notionary.elements.todo_lists import TodoElement
from notionary.elements.list_element import (
    BulletedListElement,
    NumberedListElement,
)
from notionary.elements.qoute_element import QuoteElement
from notionary.elements.image_element import ImageElement
from notionary.elements.video_element import VideoElement
from notionary.elements.toggle_element import ToggleElement
from notionary.elements.bookmark_element import BookmarkElement
from notionary.elements.column_element import ColumnElement


class BlockElementRegistryBuilder:
    """
    True builder for constructing BlockElementRegistry instances.

    This builder allows for incremental construction of registry instances
    with specific configurations of block elements.
    """

    def __init__(self):
        """Initialize a new builder with an empty element list."""
        self._elements = OrderedDict()

    @classmethod
    def start_empty(cls) -> BlockElementRegistryBuilder:
        """
        Start with a completely empty registry builder.

        Returns:
            A new builder instance with no elements
        """
        return cls()

    @classmethod
    def start_minimal(cls) -> BlockElementRegistryBuilder:
        """
        Start with a minimal set of essential elements.

        Returns:
            A new builder instance with basic elements
        """
        builder = cls()
        return builder.with_headings().with_lists().with_paragraphs()

    @classmethod
    def start_standard(cls) -> BlockElementRegistryBuilder:
        """
        Start with all standard elements in recommended order.

        Returns:
            A new builder instance with all standard elements
        """
        builder = cls()
        return (
            builder.with_headings()
            .with_callouts()
            .with_code()
            .with_dividers()
            .with_tables()
            .with_columns()
            .with_lists()
            .with_toggles()
            .with_quotes()
            .with_todos()
            .with_bookmarks()
            .with_images()
            .with_videos()
            .with_embeds()
            .with_audio()
            .with_mention()
            .with_paragraphs()
        )

    # Element manipulation methods

    def add_element(
        self, element_class: Type[NotionBlockElement]
    ) -> BlockElementRegistryBuilder:
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
    ) -> BlockElementRegistryBuilder:
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
    ) -> BlockElementRegistryBuilder:
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
    ) -> BlockElementRegistryBuilder:
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

    def with_paragraphs(self) -> BlockElementRegistryBuilder:
        """
        Add support for paragraph elements.

        Returns:
            Self for method chaining
        """
        return self.add_element(ParagraphElement)

    def with_headings(self) -> BlockElementRegistryBuilder:
        """
        Add support for heading elements.

        Returns:
            Self for method chaining
        """
        return self.add_element(HeadingElement)

    def with_callouts(self) -> BlockElementRegistryBuilder:
        """
        Add support for callout elements.

        Returns:
            Self for method chaining
        """
        return self.add_element(CalloutElement)

    def with_code(self) -> BlockElementRegistryBuilder:
        """
        Add support for code blocks.

        Returns:
            Self for method chaining
        """
        return self.add_element(CodeBlockElement)

    def with_dividers(self) -> BlockElementRegistryBuilder:
        """
        Add support for divider elements.

        Returns:
            Self for method chaining
        """
        return self.add_element(DividerElement)

    def with_tables(self) -> BlockElementRegistryBuilder:
        """
        Add support for tables.

        Returns:
            Self for method chaining
        """
        return self.add_element(TableElement)

    def with_columns(self) -> BlockElementRegistryBuilder:
        """
        Add support for column elements.

        Returns:
            Self for method chaining
        """
        return self.add_element(ColumnElement)

    def with_lists(self) -> BlockElementRegistryBuilder:
        """
        Add support for list elements.

        Returns:
            Self for method chaining
        """
        return self.add_element(BulletedListElement).add_element(NumberedListElement)

    def with_toggles(self) -> BlockElementRegistryBuilder:
        """
        Add support for toggle elements.

        Returns:
            Self for method chaining
        """
        return self.add_element(ToggleElement)

    def with_quotes(self) -> BlockElementRegistryBuilder:
        """
        Add support for quote elements.

        Returns:
            Self for method chaining
        """
        return self.add_element(QuoteElement)

    def with_todos(self) -> BlockElementRegistryBuilder:
        """
        Add support for todo elements.

        Returns:
            Self for method chaining
        """
        return self.add_element(TodoElement)

    def with_bookmarks(self) -> BlockElementRegistryBuilder:
        """
        Add support for bookmark elements.

        Returns:
            Self for method chaining
        """
        return self.add_element(BookmarkElement)

    def with_images(self) -> BlockElementRegistryBuilder:
        """
        Add support for image elements.

        Returns:
            Self for method chaining
        """
        return self.add_element(ImageElement)

    def with_videos(self) -> BlockElementRegistryBuilder:
        """
        Add support for video elements.

        Returns:
            Self for method chaining
        """
        return self.add_element(VideoElement)

    def with_embeds(self) -> BlockElementRegistryBuilder:
        """
        Add support for embed elements.

        Returns:
            Self for method chaining
        """
        return self.add_element(EmbedElement)

    def with_audio(self) -> BlockElementRegistryBuilder:
        """
        Add support for audio elements.

        Returns:
            Self for method chaining
        """
        return self.add_element(AudioElement)

    def with_media_support(self) -> BlockElementRegistryBuilder:
        """
        Add support for media elements (images, videos, audio).

        Returns:
            Self for method chaining
        """
        return self.with_images().with_videos().with_audio()

    def with_mention(self) -> BlockElementRegistryBuilder:
        return self.add_element(MentionElement)

    def build(self) -> BlockElementRegistry:
        """
        Build and return the configured BlockElementRegistry instance.

        This automatically ensures that ParagraphElement is at the end
        of the registry (if present) as a fallback element, unless
        this behavior was explicitly disabled.

        Returns:
            A configured BlockElementRegistry instance
        """
        if ParagraphElement.__name__ not in self._elements:
            # Add paragraph as fallback if not present
            self.add_element(ParagraphElement)
        else:
            # Ensure it's at the end
            self._ensure_paragraph_at_end()

        registry = BlockElementRegistry()

        # Add elements in the recorded order
        for element_class in self._elements.values():
            registry.register(element_class)

        return registry

    @classmethod
    def create_standard_registry(cls) -> BlockElementRegistry:
        """
        Factory method to directly create a standard registry.

        Returns:
            A fully configured registry instance
        """
        return cls.start_standard().build()

    @classmethod
    def create_minimal_registry(cls) -> BlockElementRegistry:
        """
        Factory method to directly create a minimal registry.

        Returns:
            A minimal registry instance
        """
        return cls.start_minimal().build()

    @classmethod
    def create_custom_registry(
        cls, element_classes: List[Type[NotionBlockElement]]
    ) -> BlockElementRegistry:
        """
        Factory method to directly create a custom registry.

        Args:
            element_classes: List of element classes to register

        Returns:
            A custom configured registry instance
        """
        return cls().add_elements(element_classes).build()
