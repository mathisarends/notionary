from __future__ import annotations

from typing import Literal, Optional, Union

from pydantic import BaseModel, Field

# Die Frage ist braucht man hier diese models hier überhaupt (der type ist ein Diskriminator aber es könnte auch über die Signatur abgeleitet werden.)
class HeadingProcessorModel(BaseModel):
    type: Literal["heading"] = "heading"
    text: str
    level: int = 2


class ParagraphProcessorModel(BaseModel):
    type: Literal["paragraph"] = "paragraph"
    text: str


class QuoteProcessorModel(BaseModel):
    type: Literal["quote"] = "quote"
    text: str


class BulletedListProcessorModel(BaseModel):
    type: Literal["bulleted_list"] = "bulleted_list"
    texts: list[str]


class NumberedListProcessorModel(BaseModel):
    type: Literal["numbered_list"] = "numbered_list"
    texts: list[str]


class TodoProcessorModel(BaseModel):
    type: Literal["todo"] = "todo"
    text: str
    checked: bool = False


class CalloutProcessorModel(BaseModel):
    type: Literal["callout"] = "callout"
    text: str
    emoji: Optional[str] = None


class CodeProcessorModel(BaseModel):
    type: Literal["code"] = "code"
    code: str
    language: Optional[str] = None
    caption: Optional[str] = None


class ImageProcessorModel(BaseModel):
    type: Literal["image"] = "image"
    url: str
    caption: Optional[str] = None
    alt: Optional[str] = None


class VideoProcessorModel(BaseModel):
    type: Literal["video"] = "video"
    url: str
    caption: Optional[str] = None


class AudioProcessorModel(BaseModel):
    type: Literal["audio"] = "audio"
    url: str
    caption: Optional[str] = None


class FileProcessorModel(BaseModel):
    type: Literal["file"] = "file"
    url: str
    caption: Optional[str] = None


class PdfProcessorModel(BaseModel):
    type: Literal["pdf"] = "pdf"
    url: str
    caption: Optional[str] = None


class BookmarkProcessorModel(BaseModel):
    type: Literal["bookmark"] = "bookmark"
    url: str
    title: Optional[str] = None
    caption: Optional[str] = None


class EmbedProcessorModel(BaseModel):
    type: Literal["embed"] = "embed"
    url: str
    caption: Optional[str] = None


class TableProcessorModel(BaseModel):
    type: Literal["table"] = "table"
    headers: list[str]
    rows: list[list[str]]


class DividerProcessorModel(BaseModel):
    type: Literal["divider"] = "divider"


class EquationProcessorModel(BaseModel):
    type: Literal["equation"] = "equation"
    expression: str


class TableOfContentsProcessorModel(BaseModel):
    type: Literal["table_of_contents"] = "table_of_contents"
    color: Optional[str] = None


# Special blocks for nested content
class ToggleProcessorModel(BaseModel):
    type: Literal["toggle"] = "toggle"
    title: str
    children: list[MarkdownBlock] = Field(default_factory=list)


class ToggleableHeadingProcessorModel(BaseModel):
    type: Literal["toggleable_heading"] = "toggleable_heading"
    text: str
    level: int = Field(ge=1, le=3)
    children: list[MarkdownBlock] = Field(default_factory=list)


class ColumnProcessorModel(BaseModel):
    type: Literal["columns"] = "columns"
    columns: list[list[MarkdownBlock]] = Field(default_factory=list)
    width_ratios: Optional[list[float]] = None


class BreadcrumbProcessorModel(BaseModel):
    type: Literal["breadcrumb"] = "breadcrumb"


# Union of all possible blocks
MarkdownBlock = Union[
    HeadingProcessorModel,
    ParagraphProcessorModel,
    QuoteProcessorModel,
    BulletedListProcessorModel,
    NumberedListProcessorModel,
    TodoProcessorModel,
    CalloutProcessorModel,
    CodeProcessorModel,
    ImageProcessorModel,
    VideoProcessorModel,
    AudioProcessorModel,
    FileProcessorModel,
    PdfProcessorModel,
    BookmarkProcessorModel,
    EmbedProcessorModel,
    TableProcessorModel,
    DividerProcessorModel,
    EquationProcessorModel,
    TableOfContentsProcessorModel,
    ToggleProcessorModel,
    ToggleableHeadingProcessorModel,
    ColumnProcessorModel,
    BreadcrumbProcessorModel,
]


# Update forward references for nested structures
ToggleProcessorModel.model_rebuild()
ToggleableHeadingProcessorModel.model_rebuild()
ColumnProcessorModel.model_rebuild()


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
