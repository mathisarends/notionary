from __future__ import annotations

from collections import OrderedDict
from typing import ClassVar

from notionary.blocks.mappings import (
    AudioElement,
    BaseBlockElement,
    BookmarkElement,
    BreadcrumbElement,
    BulletedListElement,
    CalloutElement,
    ChildDatabaseElement,
    CodeElement,
    ColumnElement,
    ColumnListElement,
    DividerElement,
    EmbedElement,
    EquationElement,
    FileElement,
    HeadingElement,
    ImageElement,
    NumberedListElement,
    ParagraphElement,
    PdfElement,
    QuoteElement,
    SpaceElement,
    TableElement,
    TableOfContentsElement,
    TodoElement,
    ToggleableHeadingElement,
    ToggleElement,
    VideoElement,
)


class BlockRegistry:
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
        self._elements = OrderedDict()
        self._excluded_elements = excluded_elements or set()

        self._initialize_default_elements()

    def _initialize_default_elements(self) -> None:
        """Initialize registry with default elements minus excluded ones."""
        for element_class in self._DEFAULT_ELEMENTS:
            if element_class not in self._excluded_elements:
                self._elements[element_class.__name__] = element_class

    def exclude_elements(self, *element_classes: type[BaseBlockElement]) -> BlockRegistry:
        new_excluded = self._excluded_elements.copy()
        new_excluded.update(element_classes)
        return BlockRegistry(excluded_elements=new_excluded)

    def register(self, element_class: type[BaseBlockElement]) -> bool:
        if element_class.__name__ in self._elements:
            return False

        self._elements[element_class.__name__] = element_class
        return True

    def remove(self, element_class: type[BaseBlockElement]) -> bool:
        return self._elements.pop(element_class.__name__, None) is not None

    def contains(self, element_class: type[BaseBlockElement]) -> bool:
        return element_class.__name__ in self._elements

    def get_elements(self) -> list[type[BaseBlockElement]]:
        return list(self._elements.values())

    def is_excluded(self, element_class: type[BaseBlockElement]) -> bool:
        return element_class in self._excluded_elements
