from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from notionary.blocks.enums import CodingLanguage

if TYPE_CHECKING:
    from notionary.page.content.markdown.structured_output.service import (
        StructuredOutputMarkdownConverter,
    )


class MarkdownNodeType(StrEnum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    SPACE = "space"
    DIVIDER = "divider"
    QUOTE = "quote"
    BULLETED_LIST = "bulleted_list"
    BULLETED_LIST_ITEM = "bulleted_list_item"
    NUMBERED_LIST = "numbered_list"
    NUMBERED_LIST_ITEM = "numbered_list_item"
    TODO = "todo"
    TODO_LIST = "todo_list"
    CALLOUT = "callout"
    TOGGLE = "toggle"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    FILE = "file"
    PDF = "pdf"
    BOOKMARK = "bookmark"
    EMBED = "embed"
    CODE = "code"
    MERMAID = "mermaid"
    TABLE = "table"
    BREADCRUMB = "breadcrumb"
    EQUATION = "equation"
    TABLE_OF_CONTENTS = "table_of_contents"
    COLUMNS = "columns"


class MarkdownNodeSchema(BaseModel):
    type: MarkdownNodeType

    def process_with(self, processor: StructuredOutputMarkdownConverter) -> None:
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement process_with()"
        )


class ParagraphSchema(MarkdownNodeSchema):
    type: Literal[MarkdownNodeType.PARAGRAPH] = MarkdownNodeType.PARAGRAPH
    text: str = Field(description="The paragraph text content")

    def process_with(self, processor: StructuredOutputMarkdownConverter) -> None:
        processor._process_paragraph(self)


class HeadingSchema(MarkdownNodeSchema):
    type: Literal[MarkdownNodeType.HEADING] = MarkdownNodeType.HEADING
    text: str = Field(description="The heading text")
    level: Literal[1, 2, 3] = Field(description="Heading level (1-3)")
    children: list[MarkdownNodeSchema] | None = Field(
        default=None, description="Optional child nodes"
    )

    def process_with(self, processor: StructuredOutputMarkdownConverter) -> None:
        processor._process_heading(self)


class SpaceSchema(MarkdownNodeSchema):
    type: Literal[MarkdownNodeType.SPACE] = MarkdownNodeType.SPACE

    def process_with(self, processor: StructuredOutputMarkdownConverter) -> None:
        processor._process_space()


class DividerSchema(MarkdownNodeSchema):
    type: Literal[MarkdownNodeType.DIVIDER] = MarkdownNodeType.DIVIDER

    def process_with(self, processor: StructuredOutputMarkdownConverter) -> None:
        processor._process_divider()


class QuoteSchema(MarkdownNodeSchema):
    type: Literal[MarkdownNodeType.QUOTE] = MarkdownNodeType.QUOTE
    text: str = Field(description="The quote text")
    children: list[MarkdownNodeSchema] | None = Field(
        default=None, description="Optional child nodes"
    )

    def process_with(self, processor: StructuredOutputMarkdownConverter) -> None:
        processor._process_quote(self)


class BulletedListSchema(MarkdownNodeSchema):
    type: Literal[MarkdownNodeType.BULLETED_LIST] = MarkdownNodeType.BULLETED_LIST
    items: list[str] = Field(description="List of bullet point texts")

    def process_with(self, processor: StructuredOutputMarkdownConverter) -> None:
        processor._process_bulleted_list(self)


class BulletedListItemSchema(MarkdownNodeSchema):
    type: Literal[MarkdownNodeType.BULLETED_LIST_ITEM] = (
        MarkdownNodeType.BULLETED_LIST_ITEM
    )
    text: str = Field(description="The bullet point text")
    children: list[MarkdownNodeSchema] | None = Field(
        default=None, description="Optional nested content"
    )

    def process_with(self, processor: StructuredOutputMarkdownConverter) -> None:
        processor._process_bulleted_list_item(self)


class NumberedListSchema(MarkdownNodeSchema):
    type: Literal[MarkdownNodeType.NUMBERED_LIST] = MarkdownNodeType.NUMBERED_LIST
    items: list[str] = Field(description="List of numbered item texts")

    def process_with(self, processor: StructuredOutputMarkdownConverter) -> None:
        processor._process_numbered_list(self)


class NumberedListItemSchema(MarkdownNodeSchema):
    type: Literal[MarkdownNodeType.NUMBERED_LIST_ITEM] = (
        MarkdownNodeType.NUMBERED_LIST_ITEM
    )
    text: str = Field(description="The numbered item text")
    children: list[MarkdownNodeSchema] | None = Field(
        default=None, description="Optional nested content"
    )

    def process_with(self, processor: StructuredOutputMarkdownConverter) -> None:
        processor._process_numbered_list_item(self)


class TodoSchema(MarkdownNodeSchema):
    type: Literal[MarkdownNodeType.TODO] = MarkdownNodeType.TODO
    text: str = Field(description="The todo item text")
    checked: bool = Field(default=False, description="Whether the todo is completed")
    children: list[MarkdownNodeSchema] | None = Field(
        default=None, description="Optional nested content"
    )

    def process_with(self, processor: StructuredOutputMarkdownConverter) -> None:
        processor._process_todo(self)


class TodoListSchema(MarkdownNodeSchema):
    type: Literal[MarkdownNodeType.TODO_LIST] = MarkdownNodeType.TODO_LIST
    items: list[str] = Field(description="List of todo item texts")
    completed: list[bool] | None = Field(
        default=None, description="List indicating which items are completed"
    )

    def process_with(self, processor: StructuredOutputMarkdownConverter) -> None:
        processor._process_todo_list(self)


class CalloutSchema(MarkdownNodeSchema):
    type: Literal[MarkdownNodeType.CALLOUT] = MarkdownNodeType.CALLOUT
    text: str = Field(description="The callout text")
    emoji: str | None = Field(default=None, description="Optional emoji icon")
    children: list[MarkdownNodeSchema] | None = Field(
        default=None, description="Optional child nodes"
    )

    def process_with(self, processor: StructuredOutputMarkdownConverter) -> None:
        processor._process_callout(self)


class ToggleSchema(MarkdownNodeSchema):
    type: Literal[MarkdownNodeType.TOGGLE] = MarkdownNodeType.TOGGLE
    title: str = Field(description="The toggle title")
    children: list[MarkdownNodeSchema] = Field(description="Content inside the toggle")

    def process_with(self, processor: StructuredOutputMarkdownConverter) -> None:
        processor._process_toggle(self)


class ImageSchema(MarkdownNodeSchema):
    type: Literal[MarkdownNodeType.IMAGE] = MarkdownNodeType.IMAGE
    url: str = Field(description="Image URL")
    caption: str | None = Field(default=None, description="Optional caption")

    def process_with(self, processor: StructuredOutputMarkdownConverter) -> None:
        processor._process_image(self)


class VideoSchema(MarkdownNodeSchema):
    type: Literal[MarkdownNodeType.VIDEO] = MarkdownNodeType.VIDEO
    url: str = Field(description="Video URL")
    caption: str | None = Field(default=None, description="Optional caption")

    def process_with(self, processor: StructuredOutputMarkdownConverter) -> None:
        processor._process_video(self)


class AudioSchema(MarkdownNodeSchema):
    type: Literal[MarkdownNodeType.AUDIO] = MarkdownNodeType.AUDIO
    url: str = Field(description="Audio URL")
    caption: str | None = Field(default=None, description="Optional caption")

    def process_with(self, processor: StructuredOutputMarkdownConverter) -> None:
        processor._process_audio(self)


class FileSchema(MarkdownNodeSchema):
    type: Literal[MarkdownNodeType.FILE] = MarkdownNodeType.FILE
    url: str = Field(description="File URL")
    caption: str | None = Field(default=None, description="Optional caption")

    def process_with(self, processor: StructuredOutputMarkdownConverter) -> None:
        processor._process_file(self)


class PdfSchema(MarkdownNodeSchema):
    type: Literal[MarkdownNodeType.PDF] = MarkdownNodeType.PDF
    url: str = Field(description="PDF URL")
    caption: str | None = Field(default=None, description="Optional caption")

    def process_with(self, processor: StructuredOutputMarkdownConverter) -> None:
        processor._process_pdf(self)


class BookmarkSchema(MarkdownNodeSchema):
    type: Literal[MarkdownNodeType.BOOKMARK] = MarkdownNodeType.BOOKMARK
    url: str = Field(description="Bookmark URL")
    title: str | None = Field(default=None, description="Optional title")
    caption: str | None = Field(default=None, description="Optional caption")

    def process_with(self, processor: StructuredOutputMarkdownConverter) -> None:
        processor._process_bookmark(self)


class EmbedSchema(MarkdownNodeSchema):
    type: Literal[MarkdownNodeType.EMBED] = MarkdownNodeType.EMBED
    url: str = Field(description="Embed URL")
    caption: str | None = Field(default=None, description="Optional caption")

    def process_with(self, processor: StructuredOutputMarkdownConverter) -> None:
        processor._process_embed(self)


class CodeSchema(MarkdownNodeSchema):
    type: Literal[MarkdownNodeType.CODE] = MarkdownNodeType.CODE
    code: str = Field(description="Code content")
    language: CodingLanguage | None = Field(
        default=None, description="Programming language"
    )
    caption: str | None = Field(default=None, description="Optional caption")

    def process_with(self, processor: StructuredOutputMarkdownConverter) -> None:
        processor._process_code(self)


class MermaidSchema(MarkdownNodeSchema):
    type: Literal[MarkdownNodeType.MERMAID] = MarkdownNodeType.MERMAID
    diagram: str = Field(description="Mermaid diagram code")
    caption: str | None = Field(default=None, description="Optional caption")

    def process_with(self, processor: StructuredOutputMarkdownConverter) -> None:
        processor._process_mermaid(self)


class TableSchema(MarkdownNodeSchema):
    type: Literal[MarkdownNodeType.TABLE] = MarkdownNodeType.TABLE
    headers: list[str] = Field(description="Table header row")
    rows: list[list[str]] = Field(description="Table data rows")

    def process_with(self, processor: StructuredOutputMarkdownConverter) -> None:
        processor._process_table(self)


class BreadcrumbSchema(MarkdownNodeSchema):
    type: Literal[MarkdownNodeType.BREADCRUMB] = MarkdownNodeType.BREADCRUMB

    def process_with(self, processor: StructuredOutputMarkdownConverter) -> None:
        processor._process_breadcrumb(self)


class EquationSchema(MarkdownNodeSchema):
    type: Literal[MarkdownNodeType.EQUATION] = MarkdownNodeType.EQUATION
    expression: str = Field(description="LaTeX equation expression")

    def process_with(self, processor: StructuredOutputMarkdownConverter) -> None:
        processor._process_equation(self)


class TableOfContentsSchema(MarkdownNodeSchema):
    type: Literal[MarkdownNodeType.TABLE_OF_CONTENTS] = (
        MarkdownNodeType.TABLE_OF_CONTENTS
    )

    def process_with(self, processor: StructuredOutputMarkdownConverter) -> None:
        processor._process_table_of_contents(self)


class ColumnSchema(BaseModel):
    width_ratio: float | None = Field(default=None, description="Optional width ratio")
    children: list[MarkdownNodeSchema] = Field(description="Column content")


class ColumnsSchema(MarkdownNodeSchema):
    type: Literal[MarkdownNodeType.COLUMNS] = MarkdownNodeType.COLUMNS
    columns: list[ColumnSchema] = Field(description="List of columns")

    def process_with(self, processor: StructuredOutputMarkdownConverter) -> None:
        processor._process_columns(self)


AnyMarkdownNode = Annotated[
    HeadingSchema
    | ParagraphSchema
    | SpaceSchema
    | DividerSchema
    | QuoteSchema
    | BulletedListSchema
    | BulletedListItemSchema
    | NumberedListSchema
    | NumberedListItemSchema
    | TodoSchema
    | TodoListSchema
    | CalloutSchema
    | ToggleSchema
    | ImageSchema
    | VideoSchema
    | AudioSchema
    | FileSchema
    | PdfSchema
    | BookmarkSchema
    | EmbedSchema
    | CodeSchema
    | MermaidSchema
    | TableSchema
    | BreadcrumbSchema
    | EquationSchema
    | TableOfContentsSchema
    | ColumnsSchema,
    Field(discriminator="type"),
]


class MarkdownDocumentSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodes: list[AnyMarkdownNode] = Field(
        description="List of markdown nodes in the document"
    )


class OpenAIMarkdownNode(BaseModel):
    """Flat node schema for OpenAI structured outputs - supports all node types"""

    type: MarkdownNodeType = Field(description="Type of markdown node")

    # Content fields
    text: str | None = Field(
        default=None, description="Text for paragraph, quote, list items, callout"
    )
    title: str | None = Field(default=None, description="Title for toggle or bookmark")
    expression: str | None = Field(
        default=None, description="LaTeX expression for equations"
    )
    code: str | None = Field(default=None, description="Code content")
    diagram: str | None = Field(default=None, description="Mermaid diagram")

    # List fields
    items: list[str] | None = Field(default=None, description="Items for lists")

    # Properties
    level: Literal[1, 2, 3] | None = Field(default=None, description="Heading level")
    checked: bool | None = Field(default=None, description="Todo checked status")
    completed: list[bool] | None = Field(
        default=None, description="Todo list completion"
    )
    emoji: str | None = Field(default=None, description="Callout emoji")

    # Media
    url: str | None = Field(default=None, description="URL for media/links")
    caption: str | None = Field(default=None, description="Caption for media")
    language: CodingLanguage | None = Field(default=None, description="Code language")

    # Table
    headers: list[str] | None = Field(default=None, description="Table headers")
    rows: list[list[str]] | None = Field(default=None, description="Table rows")

    # Nested
    children: list[OpenAIMarkdownNode] | None = Field(
        default=None, description="Child nodes"
    )
    columns: list[ColumnSchema] | None = Field(
        default=None, description="Column layout"
    )


class OpenAIMarkdownDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nodes: list[OpenAIMarkdownNode] = Field(description="List of markdown nodes")
