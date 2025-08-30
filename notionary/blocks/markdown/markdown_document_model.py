from __future__ import annotations

from typing import Union

from pydantic import BaseModel, Field

from notionary.blocks.heading import HeadingMarkdownNode

from notionary.blocks import (
    HeadingMarkdownNode,
    ParagraphMarkdownNode,
    QuoteMarkdownNode,
    BulletedListMarkdownNode,
    NumberedListMarkdownNode,
    TodoMarkdownNode,
    CalloutMarkdownNode,
    CodeMarkdownNode,
    ImageMarkdownNode,
    VideoMarkdownNode,
    AudioMarkdownNode,
    FileMarkdownNode,
    PdfMarkdownNode,
    BookmarkMarkdownNode,
    EmbedMarkdownNode,
    TableMarkdownNode,
    DividerMarkdownNode,
    EquationMarkdownNode,
    TableOfContentsMarkdownNode,
    ToggleMarkdownNode,
    ToggleableHeadingMarkdownNode,
    ColumnListMarkdownNode,
    BreadcrumbMarkdownNode,
)

MarkdownBlock = Union[
    HeadingMarkdownNode,
    ParagraphMarkdownNode,
    QuoteMarkdownNode,
    BulletedListMarkdownNode,
    NumberedListMarkdownNode,
    TodoMarkdownNode,
    CalloutMarkdownNode,
    CodeMarkdownNode,
    ImageMarkdownNode,
    VideoMarkdownNode,
    AudioMarkdownNode,
    FileMarkdownNode,
    PdfMarkdownNode,
    BookmarkMarkdownNode,
    EmbedMarkdownNode,
    TableMarkdownNode,
    DividerMarkdownNode,
    EquationMarkdownNode,
    TableOfContentsMarkdownNode,
    ToggleMarkdownNode,
    ToggleableHeadingMarkdownNode,
    ColumnListMarkdownNode,
    BreadcrumbMarkdownNode,
]


class MarkdownDocumentModel(BaseModel):
    """
    Complete document model for generating Markdown via MarkdownBuilder.
    Perfect for LLM structured output!
    """

    blocks: list[MarkdownBlock] = Field(default_factory=list)