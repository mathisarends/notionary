from __future__ import annotations

from typing import Literal, Optional, Union

from pydantic import BaseModel, Field

class HeadingBlock(BaseModel):
    type: Literal["heading"] = "heading"
    text: str
    level: int = 2


class ParagraphBlock(BaseModel):
    type: Literal["paragraph"] = "paragraph"
    text: str


class QuoteBlock(BaseModel):
    type: Literal["quote"] = "quote"
    text: str


class BulletedListBlock(BaseModel):
    type: Literal["bulleted_list"] = "bulleted_list"
    texts: list[str]


class NumberedListBlock(BaseModel):
    type: Literal["numbered_list"] = "numbered_list"
    texts: list[str]


class TodoBlock(BaseModel):
    type: Literal["todo"] = "todo"
    text: str
    checked: bool = False


class CalloutBlock(BaseModel):
    type: Literal["callout"] = "callout"
    text: str
    emoji: Optional[str] = None


class CodeBlock(BaseModel):
    type: Literal["code"] = "code"
    code: str
    language: Optional[str] = None
    caption: Optional[str] = None


class ImageBlock(BaseModel):
    type: Literal["image"] = "image"
    url: str
    caption: Optional[str] = None
    alt: Optional[str] = None


class VideoBlock(BaseModel):
    type: Literal["video"] = "video"
    url: str
    caption: Optional[str] = None


class AudioBlock(BaseModel):
    type: Literal["audio"] = "audio"
    url: str
    caption: Optional[str] = None


class FileBlock(BaseModel):
    type: Literal["file"] = "file"
    url: str
    caption: Optional[str] = None


class PdfBlock(BaseModel):
    type: Literal["pdf"] = "pdf"
    url: str
    caption: Optional[str] = None


class BookmarkBlock(BaseModel):
    type: Literal["bookmark"] = "bookmark"
    url: str
    title: Optional[str] = None
    caption: Optional[str] = None


class EmbedBlock(BaseModel):
    type: Literal["embed"] = "embed"
    url: str
    caption: Optional[str] = None


class TableBlock(BaseModel):
    type: Literal["table"] = "table"
    headers: list[str]
    rows: list[list[str]]


class DividerBlock(BaseModel):
    type: Literal["divider"] = "divider"


class EquationBlock(BaseModel):
    type: Literal["equation"] = "equation"
    expression: str


class TableOfContentsBlock(BaseModel):
    type: Literal["table_of_contents"] = "table_of_contents"
    color: Optional[str] = None


# Special blocks for nested content
class ToggleBlock(BaseModel):
    type: Literal["toggle"] = "toggle"
    title: str
    children: list[MarkdownBlock] = Field(default_factory=list)


class ToggleBlock(BaseModel):
    type: Literal["toggle"] = "toggle"
    title: str
    children: list[MarkdownBlock] = Field(default_factory=list)


class ToggleableHeadingBlock(BaseModel):
    type: Literal["toggleable_heading"] = "toggleable_heading"
    text: str
    level: int = Field(ge=1, le=3)
    children: list[MarkdownBlock] = Field(default_factory=list)


class ColumnBlock(BaseModel):
    type: Literal["columns"] = "columns"
    columns: list[list[MarkdownBlock]] = Field(default_factory=list)
    width_ratios: Optional[list[float]] = None


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


# Update forward references for nested structures
ToggleBlock.model_rebuild()
ToggleableHeadingBlock.model_rebuild()
ColumnBlock.model_rebuild()


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
