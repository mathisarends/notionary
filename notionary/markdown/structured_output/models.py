from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from notionary.blocks.enums import CodingLanguage

if TYPE_CHECKING:
    from notionary.markdown.structured_output import (
        StructuredOutputMarkdownConverter,
    )


class MarkdownNodeType(StrEnum):
    PARAGRAPH = "paragraph"
    HEADING_1 = "heading_1"
    HEADING_2 = "heading_2"
    HEADING_3 = "heading_3"
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


class Heading1Schema(MarkdownNodeSchema):
    type: Literal["heading_1"] = "heading_1"
    text: str = Field(description="The heading 1 text")
    children: list[MarkdownNodeSchema] | None = Field(
        default=None, description="Optional child nodes"
    )

    def process_with(self, processor: StructuredOutputMarkdownConverter) -> None:
        processor._process_heading_1(self)


class Heading2Schema(MarkdownNodeSchema):
    type: Literal["heading_2"] = "heading_2"
    text: str = Field(description="The heading 2 text")
    children: list[MarkdownNodeSchema] | None = Field(
        default=None, description="Optional child nodes"
    )

    def process_with(self, processor: StructuredOutputMarkdownConverter) -> None:
        processor._process_heading_2(self)


class Heading3Schema(MarkdownNodeSchema):
    type: Literal["heading_3"] = "heading_3"
    text: str = Field(description="The heading 3 text")
    children: list[MarkdownNodeSchema] | None = Field(
        default=None, description="Optional child nodes"
    )

    def process_with(self, processor: StructuredOutputMarkdownConverter) -> None:
        processor._process_heading_3(self)


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


class BulletedListSchema(MarkdownNodeSchema):
    type: Literal[MarkdownNodeType.BULLETED_LIST] = MarkdownNodeType.BULLETED_LIST
    items: list[BulletedListItemSchema] = Field(
        description="List of BulletedListItemSchema objects. Each item must have 'type', 'text', and optionally 'children'"
    )

    def process_with(self, processor: StructuredOutputMarkdownConverter) -> None:
        processor._process_bulleted_list(self)


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


class NumberedListSchema(MarkdownNodeSchema):
    type: Literal[MarkdownNodeType.NUMBERED_LIST] = MarkdownNodeType.NUMBERED_LIST
    items: list[NumberedListItemSchema] = Field(
        description="List of NumberedListItemSchema objects. Each item must have 'type', 'text', and optionally 'children'"
    )

    def process_with(self, processor: StructuredOutputMarkdownConverter) -> None:
        processor._process_numbered_list(self)


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
    items: list[TodoSchema] = Field(
        description="List of TodoSchema objects. Each item must have 'type', 'text', 'checked', and optionally 'children'"
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
    """Single column in a multi-column layout."""

    width_ratio: float | None = Field(
        default=None,
        description="Relative width of this column (e.g., 0.5 for half width). If not specified, columns are equal width",
    )
    children: list[MarkdownNodeSchema] = Field(
        description="Content inside this column. Can contain any markdown nodes"
    )


class ColumnsSchema(MarkdownNodeSchema):
    type: Literal[MarkdownNodeType.COLUMNS] = MarkdownNodeType.COLUMNS
    columns: list[ColumnSchema] = Field(
        description="List of columns in this layout. Each column contains its own content"
    )

    def process_with(self, processor: StructuredOutputMarkdownConverter) -> None:
        processor._process_columns(self)


type AnyMarkdownNode = Annotated[
    Heading1Schema
    | Heading2Schema
    | Heading3Schema
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
        description="Ordered list of top-level markdown nodes in the document. Each node can contain nested children"
    )
