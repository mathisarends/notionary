"""
Parameter types for MarkdownModelProcessor type hints.
These classes provide type safety for block processing methods.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from notionary.markdown.markdown_document_model import MarkdownBlock

# TODO: Brauche ich wirklich die hier und die in document models - kann ich mir fast nicht vorstellen hier
class HeadingProcessorModel(BaseModel):
    text: str
    level: int = 1


class ParagraphProcessorModel(BaseModel):
    text: str


class QuoteProcessorModel(BaseModel):
    text: str


class BulletedListProcessorModel(BaseModel):
    texts: list[str]


class NumberedListProcessorModel(BaseModel):
    texts: list[str]


class TodoProcessorModel(BaseModel):
    text: str
    checked: bool = False


class CalloutProcessorModel(BaseModel):
    text: str
    emoji: str = "💡"


class CodeProcessorModel(BaseModel):
    code: str
    language: str = ""
    caption: str = ""


class ImageProcessorModel(BaseModel):
    url: str
    caption: str = ""
    alt: str = ""


class VideoProcessorModel(BaseModel):
    url: str
    caption: str = ""


class AudioProcessorModel(BaseModel):
    url: str
    caption: str = ""


class FileProcessorModel(BaseModel):
    url: str
    caption: str = ""


class PdfProcessorModel(BaseModel):
    url: str
    caption: str = ""


class BookmarkProcessorModel(BaseModel):
    url: str
    title: str = ""
    caption: str = ""


class EmbedProcessorModel(BaseModel):
    url: str
    caption: str = ""


class TableProcessorModel(BaseModel):
    headers: list[str]
    rows: list[list[str]]


class DividerProcessorModel(BaseModel):
    pass


class ToggleProcessorModel(BaseModel):
    """Type for Toggle blocks with nested children."""

    title: str
    children: list[MarkdownBlock]  # Properly typed nested blocks


class ToggleableHeadingProcessorModel(BaseModel):
    """Type for Toggleable Heading blocks with nested children."""

    text: str
    level: int = 1
    children: list[MarkdownBlock]  # Properly typed nested blocks


class BreadcrumbProcessorModel(BaseModel):
    items: list[str]


class TableOfContentsProcessorModel(BaseModel):
    color: str = ""


class ColumnProcessorModel(BaseModel):
    """Type for Column blocks - this represents the `::: columns` container."""

    columns: list[list[MarkdownBlock]]  # Each column contains a list of blocks
    width_ratios: list[float] | None = None


class EquationProcessorModel(BaseModel):
    expression: str
