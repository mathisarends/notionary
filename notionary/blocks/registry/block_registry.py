from collections import OrderedDict
from typing import ClassVar, Self

from notionary.blocks.mappings import (
    AudioMapper,
    BookmarkMapper,
    BreadcrumbMapper,
    BulletedListMapper,
    CalloutMapper,
    CodeMapper,
    ColumnListMapper,
    DividerMapper,
    EmbedMapper,
    EquationMapper,
    FileMapper,
    HeadingMapper,
    ImageMapper,
    NotionMarkdownMapper,
    NumberedListMapper,
    ParagraphMapper,
    PdfMapper,
    QuoteMapper,
    SpaceMapper,
    TableMapper,
    TableOfContentsMapper,
    TodoMapper,
    ToggleableHeadingMapper,
    ToggleMapper,
    VideoMapper,
)


class BlockRegistry:
    _DEFAULT_ELEMENTS: ClassVar[list[type[NotionMarkdownMapper]]] = [
        HeadingMapper,
        CalloutMapper,
        CodeMapper,
        DividerMapper,
        TableMapper,
        BulletedListMapper,
        NumberedListMapper,
        ToggleMapper,
        ToggleableHeadingMapper,
        QuoteMapper,
        TodoMapper,
        BookmarkMapper,
        ImageMapper,
        VideoMapper,
        EmbedMapper,
        AudioMapper,
        ColumnListMapper,
        EquationMapper,
        TableOfContentsMapper,
        BreadcrumbMapper,
        FileMapper,
        PdfMapper,
        SpaceMapper,
        ParagraphMapper,  # Must be last as fallback!
    ]

    def __init__(self, excluded_elements: set[type[NotionMarkdownMapper]] | None = None):
        self._elements = OrderedDict()
        self._excluded_elements = excluded_elements or set()

        self._initialize_default_elements()

    def _initialize_default_elements(self) -> None:
        """Initialize registry with default elements minus excluded ones."""
        for element_class in self._DEFAULT_ELEMENTS:
            if element_class not in self._excluded_elements:
                self._elements[element_class.__name__] = element_class

    def exclude_elements(self, *element_classes: type[NotionMarkdownMapper]) -> Self:
        new_excluded = self._excluded_elements.copy()
        new_excluded.update(element_classes)
        return BlockRegistry(excluded_elements=new_excluded)

    def register(self, element_class: type[NotionMarkdownMapper]) -> bool:
        if element_class.__name__ in self._elements:
            return False

        self._elements[element_class.__name__] = element_class
        return True

    def remove(self, element_class: type[NotionMarkdownMapper]) -> bool:
        return self._elements.pop(element_class.__name__, None) is not None

    def contains(self, element_class: type[NotionMarkdownMapper]) -> bool:
        return element_class.__name__ in self._elements

    def get_elements(self) -> list[type[NotionMarkdownMapper]]:
        return list(self._elements.values())

    def is_excluded(self, element_class: type[NotionMarkdownMapper]) -> bool:
        return element_class in self._excluded_elements
