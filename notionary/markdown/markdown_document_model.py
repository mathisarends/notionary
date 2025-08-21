from __future__ import annotations

from typing import Literal, Optional, Union

from pydantic import BaseModel, Field

from notionary.blocks.bookmark.bookmark_markdown_node import \
    BookmarkMarkdownBlockParams
from notionary.blocks.bulleted_list.bulleted_list_markdown_node import \
    BulletedListMarkdownBlockParams
from notionary.blocks.callout.callout_markdown_node import \
    CalloutMarkdownBlockParams
from notionary.blocks.divider.divider_markdown_node import \
    DividerMarkdownBlockParams
from notionary.blocks.embed.embed_markdown_node import EmbedMarkdownBlockParams
from notionary.blocks.equation.equation_element_markdown_node import \
    EquationMarkdownBlockParams
from notionary.blocks.file.file_element_markdown_node import \
    FileMarkdownNodeParams
# Import all the existing params models
from notionary.blocks.heading.heading_markdown_node import \
    HeadingMarkdownBlockParams
from notionary.blocks.image_block.image_markdown_node import \
    ImageMarkdownBlockParams
from notionary.blocks.numbered_list.numbered_list_markdown_node import \
    NumberedListMarkdownBlockParams
from notionary.blocks.paragraph.paragraph_markdown_node import \
    ParagraphMarkdownBlockParams
from notionary.blocks.quote.quote_markdown_node import QuoteMarkdownBlockParams
from notionary.blocks.table.table_markdown_node import TableMarkdownBlockParams
from notionary.blocks.table_of_contents.table_of_contents_markdown_node import \
    TableOfContentsMarkdownBlockParams
from notionary.blocks.todo.todo_markdown_node import TodoMarkdownBlockParams
from notionary.blocks.video.video_markdown_node import VideoMarkdownBlockParams


class HeadingBlock(BaseModel):
    type: Literal["heading"] = "heading"
    params: HeadingMarkdownBlockParams


class ParagraphBlock(BaseModel):
    type: Literal["paragraph"] = "paragraph"
    params: ParagraphMarkdownBlockParams


class QuoteBlock(BaseModel):
    type: Literal["quote"] = "quote"
    params: QuoteMarkdownBlockParams


class BulletedListBlock(BaseModel):
    type: Literal["bulleted_list"] = "bulleted_list"
    params: BulletedListMarkdownBlockParams


class NumberedListBlock(BaseModel):
    type: Literal["numbered_list"] = "numbered_list"
    params: NumberedListMarkdownBlockParams


class TodoBlock(BaseModel):
    type: Literal["todo"] = "todo"
    params: TodoMarkdownBlockParams


class CalloutBlock(BaseModel):
    type: Literal["callout"] = "callout"
    params: CalloutMarkdownBlockParams


class CodeBlock(BaseModel):
    type: Literal["code"] = "code"
    params: CodeBlock


class ImageBlock(BaseModel):
    type: Literal["image"] = "image"
    params: ImageMarkdownBlockParams


class VideoBlock(BaseModel):
    type: Literal["video"] = "video"
    params: VideoMarkdownBlockParams


class AudioBlock(BaseModel):
    type: Literal["audio"] = "audio"
    params: FileMarkdownNodeParams


class FileBlock(BaseModel):
    type: Literal["file"] = "file"
    params: FileMarkdownNodeParams


class PdfBlock(BaseModel):
    type: Literal["pdf"] = "pdf"
    params: FileMarkdownNodeParams


class BookmarkBlock(BaseModel):
    type: Literal["bookmark"] = "bookmark"
    params: BookmarkMarkdownBlockParams


class EmbedBlock(BaseModel):
    type: Literal["embed"] = "embed"
    params: EmbedMarkdownBlockParams


class TableBlock(BaseModel):
    type: Literal["table"] = "table"
    params: TableMarkdownBlockParams


class DividerBlock(BaseModel):
    type: Literal["divider"] = "divider"
    params: DividerMarkdownBlockParams


class EquationBlock(BaseModel):
    type: Literal["equation"] = "equation"
    params: EquationMarkdownBlockParams


class TableOfContentsBlock(BaseModel):
    type: Literal["table_of_contents"] = "table_of_contents"
    params: TableOfContentsMarkdownBlockParams


# Special blocks for nested content
class ToggleBlockParams(BaseModel):
    title: str
    children: list[MarkdownBlock] = Field(default_factory=list)


class ToggleBlock(BaseModel):
    type: Literal["toggle"] = "toggle"
    params: ToggleBlockParams


class ToggleableHeadingBlockParams(BaseModel):
    text: str
    level: int = Field(ge=1, le=3)
    children: list[MarkdownBlock] = Field(default_factory=list)


class ToggleableHeadingBlock(BaseModel):
    type: Literal["toggleable_heading"] = "toggleable_heading"
    params: ToggleableHeadingBlockParams


class ColumnBlockParams(BaseModel):
    columns: list[list[MarkdownBlock]] = Field(default_factory=list)
    width_ratios: Optional[list[float]] = None


class ColumnBlock(BaseModel):
    type: Literal["columns"] = "columns"
    params: ColumnBlockParams


# Union of all possible blocks
MarkdownBlock = Union[
    HeadingBlock,
    ParagraphBlock,
    QuoteBlock,
    BulletedListBlock,
    NumberedListBlock,
    TodoBlock,
    CalloutBlock,
    CodeBlock,
    ImageBlock,
    VideoBlock,
    AudioBlock,
    FileBlock,
    PdfBlock,
    BookmarkBlock,
    EmbedBlock,
    TableBlock,
    DividerBlock,
    EquationBlock,
    TableOfContentsBlock,
    ToggleBlock,
    ToggleableHeadingBlock,
    ColumnBlock,
]


# Update forward references
ToggleBlockParams.model_rebuild()
ToggleableHeadingBlockParams.model_rebuild()
ColumnBlockParams.model_rebuild()


class MarkdownDocumentModel(BaseModel):
    """
    Complete document model for generating Markdown via MarkdownBuilder.
    Perfect for LLM structured output!

    Example:
        {
            "blocks": [
                {
                    "type": "heading",
                    "params": {"text": "My Document", "level": 1}
                },
                {
                    "type": "paragraph",
                    "params": {"text": "Introduction text"}
                },
                {
                    "type": "pdf",
                    "params": {"url": "https://example.com/doc.pdf", "caption": "Important PDF"}
                }
            ]
        }
    """

    blocks: list[MarkdownBlock] = Field(default_factory=list)

    def to_markdown(self) -> str:
        """Convert the model directly to markdown string."""
        from notionary.markdown.markdown_builder import MarkdownBuilder

        builder = MarkdownBuilder.from_model(self)
        return builder.build()
