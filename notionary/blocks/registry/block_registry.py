from __future__ import annotations

from collections import OrderedDict
from typing import ClassVar

from notionary.blocks.audio import AudioElement
from notionary.blocks.base_block_element import BaseBlockElement
from notionary.blocks.bookmark import BookmarkElement
from notionary.blocks.breadcrumbs import BreadcrumbElement
from notionary.blocks.bulleted_list import BulletedListElement
from notionary.blocks.callout import CalloutElement
from notionary.blocks.child_database import ChildDatabaseElement
from notionary.blocks.code import CodeElement
from notionary.blocks.column import ColumnElement, ColumnListElement
from notionary.blocks.divider import DividerElement
from notionary.blocks.embed import EmbedElement
from notionary.blocks.equation import EquationElement
from notionary.blocks.file import FileElement
from notionary.blocks.heading import HeadingElement
from notionary.blocks.image_block import ImageElement
from notionary.blocks.numbered_list import NumberedListElement
from notionary.blocks.paragraph import ParagraphElement
from notionary.blocks.pdf import PdfElement
from notionary.blocks.quote import QuoteElement
from notionary.blocks.space import SpaceElement
from notionary.blocks.table import TableElement
from notionary.blocks.table_of_contents import TableOfContentsElement
from notionary.blocks.todo import TodoElement
from notionary.blocks.toggle import ToggleElement
from notionary.blocks.toggleable_heading import ToggleableHeadingElement
from notionary.blocks.video import VideoElement


class BlockRegistry:
    """Registry of elements that can convert between Markdown and Notion."""

    _DEFAULT_ELEMENTS: ClassVar[list[type[BaseBlockElement]]] = [
        HeadingElement,
        CalloutElement,
        CodeElement,
        DividerElement,
        TableElement,
        BulletedListElement,
        NumberedListElement,
        ToggleElement,
        ToggleableHeadingElement,
        QuoteElement,
        TodoElement,
        BookmarkElement,
        ImageElement,
        VideoElement,
        EmbedElement,
        AudioElement,
        ColumnListElement,
        ColumnElement,
        EquationElement,
        TableOfContentsElement,
        BreadcrumbElement,
        ChildDatabaseElement,
        FileElement,
        PdfElement,
        SpaceElement,
        ParagraphElement,  # Must be last as fallback!
    ]

    def __init__(self, excluded_elements: set[type[BaseBlockElement]] | None = None):
        """
        Initialize a new registry instance.

        Args:
            excluded_elements: Set of element classes to exclude from the registry
        """
        self._elements = OrderedDict()
        self._excluded_elements = excluded_elements or set()

        self._initialize_default_elements()

    def _initialize_default_elements(self) -> None:
        """Initialize registry with default elements minus excluded ones."""
        for element_class in self._DEFAULT_ELEMENTS:
            if element_class not in self._excluded_elements:
                self._elements[element_class.__name__] = element_class

    def exclude_elements(self, *element_classes: type[BaseBlockElement]) -> BlockRegistry:
        """
        Create a new registry with additional excluded elements.

        Args:
            element_classes: Element classes to exclude

        Returns:
            New BlockRegistry instance with excluded elements
        """
        new_excluded = self._excluded_elements.copy()
        new_excluded.update(element_classes)
        return BlockRegistry(excluded_elements=new_excluded)

    def register(self, element_class: type[BaseBlockElement]) -> bool:
        """
        Register an element class.

        Args:
            element_class: The element class to register

        Returns:
            True if element was added, False if it already existed
        """
        if element_class.__name__ in self._elements:
            return False

        self._elements[element_class.__name__] = element_class
        return True

    def remove(self, element_class: type[BaseBlockElement]) -> bool:
        """
        Remove an element class.
        """
        return self._elements.pop(element_class.__name__, None) is not None

    def contains(self, element_class: type[BaseBlockElement]) -> bool:
        """
        Checks if a specific element is contained in the registry.
        """
        return element_class.__name__ in self._elements

    def get_elements(self) -> list[type[BaseBlockElement]]:
        """Get all registered elements in order."""
        return list(self._elements.values())

    def is_excluded(self, element_class: type[BaseBlockElement]) -> bool:
        """
        Check if an element class is excluded.
        """
        return element_class in self._excluded_elements
