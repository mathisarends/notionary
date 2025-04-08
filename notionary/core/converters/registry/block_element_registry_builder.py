from typing import List, Type
from collections import OrderedDict

from notionary.core.converters.elements.notion_block_element import NotionBlockElement
from notionary.core.converters.registry.block_element_registry import (
    BlockElementRegistry,
)

from notionary.core.converters.elements.paragraph_element import ParagraphElement
from notionary.core.converters.elements.heading_element import HeadingElement
from notionary.core.converters.elements.callout_element import CalloutElement
from notionary.core.converters.elements.code_block_element import CodeBlockElement
from notionary.core.converters.elements.divider_element import DividerElement
from notionary.core.converters.elements.table_element import TableElement
from notionary.core.converters.elements.todo_lists import TodoElement
from notionary.core.converters.elements.list_element import (
    BulletedListElement,
    NumberedListElement,
)
from notionary.core.converters.elements.qoute_element import QuoteElement
from notionary.core.converters.elements.image_element import ImageElement
from notionary.core.converters.elements.video_element import VideoElement
from notionary.core.converters.elements.toggle_element import ToggleElement
from notionary.core.converters.elements.bookmark_element import BookmarkElement
from notionary.core.converters.elements.column_element import ColumnElement


class BlockElementRegistryBuilder:
    """
    True builder for constructing BlockElementRegistry instances.

    This builder allows for incremental construction of registry instances
    with specific configurations of block elements.
    """

    def __init__(self):
        """Initialize a new builder with an empty element list."""
        # Use OrderedDict to maintain insertion order while ensuring uniqueness
        self._elements = OrderedDict()

    # Profile methods - create a base configuration

    @classmethod
    def start_empty(cls) -> "BlockElementRegistryBuilder":
        """
        Start with a completely empty registry builder.

        Returns:
            A new builder instance with no elements
        """
        return cls()

    @classmethod
    def start_minimal(cls) -> "BlockElementRegistryBuilder":
        """
        Start with a minimal set of essential elements.

        Returns:
            A new builder instance with basic elements
        """
        builder = cls()
        return (
            builder.add_element(HeadingElement)
            .add_element(BulletedListElement)
            .add_element(NumberedListElement)
            .add_element(ParagraphElement)
        )  # Add paragraph last as fallback

    @classmethod
    def start_standard(cls) -> "BlockElementRegistryBuilder":
        """
        Start with all standard elements in recommended order.

        Returns:
            A new builder instance with all standard elements
        """
        builder = cls()
        return (
            builder.add_element(HeadingElement)
            .add_element(CalloutElement)
            .add_element(CodeBlockElement)
            .add_element(DividerElement)
            .add_element(TableElement)
            .add_element(ColumnElement)
            .add_element(BulletedListElement)
            .add_element(NumberedListElement)
            .add_element(ToggleElement)
            .add_element(QuoteElement)
            .add_element(TodoElement)
            .add_element(BookmarkElement)
            .add_element(ImageElement)
            .add_element(VideoElement)
            .add_element(ParagraphElement)
        )  # Add paragraph last as fallback

    # Element manipulation methods

    def add_element(
        self, element_class: Type[NotionBlockElement]
    ) -> "BlockElementRegistryBuilder":
        """
        Add an element class to the registry configuration.
        If the element already exists, it's moved to the end.

        Args:
            element_class: The element class to add

        Returns:
            Self for method chaining
        """
        # Remove if exists (to update the order) and add to the end
        self._elements.pop(element_class.__name__, None)
        self._elements[element_class.__name__] = element_class
        return self

    def add_elements(
        self, element_classes: List[Type[NotionBlockElement]]
    ) -> "BlockElementRegistryBuilder":
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
    ) -> "BlockElementRegistryBuilder":
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
    ) -> "BlockElementRegistryBuilder":
        """
        Move an existing element to the end of the registry.
        If the element doesn't exist, it will be added.

        Args:
            element_class: The element class to move

        Returns:
            Self for method chaining
        """
        return self.add_element(element_class)  # add_element already handles this logic

    def ensure_paragraph_at_end(self) -> "BlockElementRegistryBuilder":
        """
        Ensure ParagraphElement is the last element in the registry.
        If it doesn't exist, it will be added.

        Returns:
            Self for method chaining
        """
        return self.move_element_to_end(ParagraphElement)

    # Specialized configuration methods

    def with_list_support(self) -> "BlockElementRegistryBuilder":
        """
        Add support for list elements.

        Returns:
            Self for method chaining
        """
        return self.add_element(BulletedListElement).add_element(NumberedListElement)

    def with_code_support(self) -> "BlockElementRegistryBuilder":
        """
        Add support for code blocks.

        Returns:
            Self for method chaining
        """
        return self.add_element(CodeBlockElement)

    def with_table_support(self) -> "BlockElementRegistryBuilder":
        """
        Add support for tables.

        Returns:
            Self for method chaining
        """
        return self.add_element(TableElement)

    def with_rich_content(self) -> "BlockElementRegistryBuilder":
        """
        Add support for rich content elements (callouts, toggles, etc.).

        Returns:
            Self for method chaining
        """
        return (
            self.add_element(CalloutElement)
            .add_element(ToggleElement)
            .add_element(QuoteElement)
        )

    def with_media_support(self) -> "BlockElementRegistryBuilder":
        """
        Add support for media elements (images, videos).

        Returns:
            Self for method chaining
        """
        return self.add_element(ImageElement).add_element(VideoElement)

    def with_task_support(self) -> "BlockElementRegistryBuilder":
        """
        Add support for task-related elements (todos).

        Returns:
            Self for method chaining
        """
        return self.add_element(TodoElement)

    def build(self) -> BlockElementRegistry:
        """
        Build and return the configured BlockElementRegistry instance.

        Returns:
            A configured BlockElementRegistry instance
        """
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
