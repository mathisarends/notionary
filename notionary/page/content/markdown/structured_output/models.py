from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from notionary.blocks.enums import BlockType, CodingLanguage


class MarkdownNodeSchema(BaseModel):
    type: str


class ParagraphSchema(MarkdownNodeSchema):
    type: Literal[BlockType.PARAGRAPH] = BlockType.PARAGRAPH
    text: str = Field(description="The paragraph text content")


class HeadingSchema(MarkdownNodeSchema):
    type: Literal[BlockType.HEADING_1, BlockType.HEADING_2, BlockType.HEADING_3] = (
        BlockType.HEADING_1
    )
    text: str = Field(description="The heading text")
    level: Literal[1, 2, 3] = Field(description="Heading level (1-3)")
    children: list[MarkdownNodeSchema] | None = Field(
        default=None, description="Optional child nodes"
    )


class SpaceSchema(MarkdownNodeSchema):
    type: Literal[BlockType.UNSUPPORTED] = BlockType.UNSUPPORTED


class DividerSchema(MarkdownNodeSchema):
    type: Literal[BlockType.DIVIDER] = BlockType.DIVIDER


class QuoteSchema(MarkdownNodeSchema):
    type: Literal[BlockType.QUOTE] = BlockType.QUOTE
    text: str = Field(description="The quote text")
    children: list[MarkdownNodeSchema] | None = Field(
        default=None, description="Optional child nodes"
    )


class BulletedListSchema(MarkdownNodeSchema):
    type: Literal[BlockType.BULLETED_LIST_ITEM] = BlockType.BULLETED_LIST_ITEM
    items: list[str] = Field(description="List of bullet point texts")


class BulletedListItemSchema(MarkdownNodeSchema):
    type: Literal[BlockType.BULLETED_LIST_ITEM] = BlockType.BULLETED_LIST_ITEM
    text: str = Field(description="The bullet point text")
    children: list[MarkdownNodeSchema] | None = Field(
        default=None, description="Optional nested content"
    )


class NumberedListSchema(MarkdownNodeSchema):
    type: Literal[BlockType.NUMBERED_LIST_ITEM] = BlockType.NUMBERED_LIST_ITEM
    items: list[str] = Field(description="List of numbered item texts")


class NumberedListItemSchema(MarkdownNodeSchema):
    type: Literal[BlockType.NUMBERED_LIST_ITEM] = BlockType.NUMBERED_LIST_ITEM
    text: str = Field(description="The numbered item text")
    children: list[MarkdownNodeSchema] | None = Field(
        default=None, description="Optional nested content"
    )


class TodoSchema(MarkdownNodeSchema):
    type: Literal[BlockType.TO_DO] = BlockType.TO_DO
    text: str = Field(description="The todo item text")
    checked: bool = Field(default=False, description="Whether the todo is completed")
    children: list[MarkdownNodeSchema] | None = Field(
        default=None, description="Optional nested content"
    )


class TodoListSchema(MarkdownNodeSchema):
    type: Literal[BlockType.TO_DO] = BlockType.TO_DO
    items: list[str] = Field(description="List of todo item texts")
    completed: list[bool] | None = Field(
        default=None, description="List indicating which items are completed"
    )


class CalloutSchema(MarkdownNodeSchema):
    type: Literal[BlockType.CALLOUT] = BlockType.CALLOUT
    text: str = Field(description="The callout text")
    emoji: str | None = Field(default=None, description="Optional emoji icon")
    children: list[MarkdownNodeSchema] | None = Field(
        default=None, description="Optional child nodes"
    )


class ToggleSchema(MarkdownNodeSchema):
    type: Literal[BlockType.TOGGLE] = BlockType.TOGGLE
    title: str = Field(description="The toggle title")
    children: list[MarkdownNodeSchema] = Field(description="Content inside the toggle")


class ImageSchema(MarkdownNodeSchema):
    type: Literal[BlockType.IMAGE] = BlockType.IMAGE
    url: str = Field(description="Image URL")
    caption: str | None = Field(default=None, description="Optional caption")


class VideoSchema(MarkdownNodeSchema):
    type: Literal[BlockType.VIDEO] = BlockType.VIDEO
    url: str = Field(description="Video URL")
    caption: str | None = Field(default=None, description="Optional caption")


class AudioSchema(MarkdownNodeSchema):
    type: Literal[BlockType.AUDIO] = BlockType.AUDIO
    url: str = Field(description="Audio URL")
    caption: str | None = Field(default=None, description="Optional caption")


class FileSchema(MarkdownNodeSchema):
    type: Literal[BlockType.FILE] = BlockType.FILE
    url: str = Field(description="File URL")
    caption: str | None = Field(default=None, description="Optional caption")


class PdfSchema(MarkdownNodeSchema):
    type: Literal[BlockType.PDF] = BlockType.PDF
    url: str = Field(description="PDF URL")
    caption: str | None = Field(default=None, description="Optional caption")


class BookmarkSchema(MarkdownNodeSchema):
    type: Literal[BlockType.BOOKMARK] = BlockType.BOOKMARK
    url: str = Field(description="Bookmark URL")
    title: str | None = Field(default=None, description="Optional title")
    caption: str | None = Field(default=None, description="Optional caption")


class EmbedSchema(MarkdownNodeSchema):
    type: Literal[BlockType.EMBED] = BlockType.EMBED
    url: str = Field(description="Embed URL")
    caption: str | None = Field(default=None, description="Optional caption")


class CodeSchema(MarkdownNodeSchema):
    type: Literal[BlockType.CODE] = BlockType.CODE
    code: str = Field(description="Code content")
    language: CodingLanguage | None = Field(
        default=None, description="Programming language"
    )
    caption: str | None = Field(default=None, description="Optional caption")


class MermaidSchema(MarkdownNodeSchema):
    type: Literal[BlockType.UNSUPPORTED] = BlockType.UNSUPPORTED
    diagram: str = Field(description="Mermaid diagram code")
    caption: str | None = Field(default=None, description="Optional caption")


class TableSchema(MarkdownNodeSchema):
    type: Literal[BlockType.TABLE] = BlockType.TABLE
    headers: list[str] = Field(description="Table header row")
    rows: list[list[str]] = Field(description="Table data rows")


class BreadcrumbSchema(MarkdownNodeSchema):
    type: Literal[BlockType.BREADCRUMB] = BlockType.BREADCRUMB


class EquationSchema(MarkdownNodeSchema):
    type: Literal[BlockType.EQUATION] = BlockType.EQUATION
    expression: str = Field(description="LaTeX equation expression")


class TableOfContentsSchema(MarkdownNodeSchema):
    type: Literal[BlockType.TABLE_OF_CONTENTS] = BlockType.TABLE_OF_CONTENTS


class ColumnSchema(BaseModel):
    width_ratio: float | None = Field(default=None, description="Optional width ratio")
    children: list[MarkdownNodeSchema] = Field(description="Column content")


class ColumnsSchema(MarkdownNodeSchema):
    type: Literal[BlockType.COLUMN_LIST] = BlockType.COLUMN_LIST
    columns: list[ColumnSchema] = Field(description="List of columns")


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
