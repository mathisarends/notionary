"""
Parameter types for MarkdownModelProcessor type hints.
These classes provide type safety for block processing methods.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from notionary.markdown.markdown_document_model import MarkdownBlock


class HeadingBlockParams(BaseModel):
    text: str
    level: int = 1


class ParagraphBlockParams(BaseModel):
    text: str


class QuoteBlockParams(BaseModel):
    text: str


class BulletedListBlockParams(BaseModel):
    texts: list[str]


class NumberedListBlockParams(BaseModel):
    texts: list[str]


class TodoBlockParams(BaseModel):
    text: str
    checked: bool = False


class CalloutBlockParams(BaseModel):
    text: str
    emoji: str = "💡"


class CodeBlockParams(BaseModel):
    code: str
    language: str = ""
    caption: str = ""


class ImageBlockParams(BaseModel):
    url: str
    caption: str = ""
    alt: str = ""


class VideoBlockParams(BaseModel):
    url: str
    caption: str = ""


class AudioBlockParams(BaseModel):
    url: str
    caption: str = ""


class FileBlockParams(BaseModel):
    url: str
    caption: str = ""


class PdfBlockParams(BaseModel):
    url: str
    caption: str = ""


class BookmarkBlockParams(BaseModel):
    url: str
    title: str = ""
    caption: str = ""


class EmbedBlockParams(BaseModel):
    url: str
    caption: str = ""


class TableBlockParams(BaseModel):
    headers: list[str]
    rows: list[list[str]]


class DividerBlockParams(BaseModel):
    pass


class ToggleBlockParams(BaseModel):
    """Type for Toggle blocks with nested children."""
    title: str
    children: list[MarkdownBlock]  # Properly typed nested blocks


class ToggleableHeadingBlockParams(BaseModel):
    """Type for Toggleable Heading blocks with nested children."""
    text: str
    level: int = 1
    children: list[MarkdownBlock]  # Properly typed nested blocks


class BreadcrumbBlockParams(BaseModel):
    items: list[str]


class TableOfContentsBlockParams(BaseModel):
    color: str = ""


class ColumnBlockParams(BaseModel):
    """Type for Column blocks - this represents the `::: columns` container."""
    columns: list[list[MarkdownBlock]]  # Each column contains a list of blocks
    width_ratios: list[float] | None = None


class EquationBlockParams(BaseModel):
    expression: str
