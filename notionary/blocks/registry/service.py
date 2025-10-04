from collections import OrderedDict
from typing import ClassVar

from notionary.blocks.mappings import (
    AudioMapper,
    BookmarkMapper,
    BreadcrumbMapper,
    BulletedListMapper,
    CalloutMapper,
    CodeMapper,
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
        QuoteMapper,
        TodoMapper,
        BookmarkMapper,
        ImageMapper,
        VideoMapper,
        EmbedMapper,
        AudioMapper,
        EquationMapper,
        TableOfContentsMapper,
        BreadcrumbMapper,
        FileMapper,
        PdfMapper,
        SpaceMapper,
        ParagraphMapper,  # Must be last as fallback!
    ]

    def __init__(self, excluded_elements: set[type[NotionMarkdownMapper]] | None = None) -> None:
        self._elements = OrderedDict()
        self._excluded_elements = excluded_elements or set()

        self._initialize_default_elements()

    def _initialize_default_elements(self) -> None:
        for element_class in self._DEFAULT_ELEMENTS:
            if element_class not in self._excluded_elements:
                self._elements[element_class.__name__] = element_class

    def get_elements(self) -> list[type[NotionMarkdownMapper]]:
        return list(self._elements.values())
