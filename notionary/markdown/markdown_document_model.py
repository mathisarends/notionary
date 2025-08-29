from __future__ import annotations

from typing import Union

from pydantic import BaseModel, Field

from notionary.blocks.heading import HeadingMarkdownNode
from notionary.blocks.paragraph import ParagraphMarkdownNode
from notionary.blocks.quote import QuoteMarkdownNode
from notionary.blocks.bulleted_list import BulletedListMarkdownNode
from notionary.blocks.numbered_list import NumberedListMarkdownNode
from notionary.blocks.todo import TodoMarkdownNode
from notionary.blocks.callout import CalloutMarkdownNode
from notionary.blocks.code import CodeMarkdownNode
from notionary.blocks.image_block import ImageMarkdownNode
from notionary.blocks.video import VideoMarkdownNode
from notionary.blocks.audio import AudioMarkdownNode
from notionary.blocks.file import FileMarkdownNode
from notionary.blocks.pdf import PdfMarkdownNode
from notionary.blocks.bookmark import BookmarkMarkdownNode
from notionary.blocks.embed import EmbedMarkdownNode
from notionary.blocks.table import TableMarkdownNode
from notionary.blocks.divider import DividerMarkdownNode
from notionary.blocks.equation import EquationMarkdownNode
from notionary.blocks.table_of_contents import TableOfContentsMarkdownNode
from notionary.blocks.toggle import ToggleMarkdownNode
from notionary.blocks.toggleable_heading import ToggleableHeadingMarkdownNode
from notionary.blocks.column import ColumnListMarkdownNode
from notionary.blocks.breadcrumbs import BreadcrumbMarkdownNode

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

    def to_markdown(self) -> str:
        """Convert the model directly to markdown string."""
        from notionary.markdown.markdown_builder import MarkdownBuilder

        builder = MarkdownBuilder.from_model(self)
        return builder.build()
