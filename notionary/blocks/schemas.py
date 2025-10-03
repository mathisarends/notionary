from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from notionary.blocks.enums import BlockColor, BlockType, CodeLanguage, FileType
from notionary.blocks.mappings.rich_text.models import RichText
from notionary.shared.models.icon_models import Icon
from notionary.shared.models.parent_models import Parent
from notionary.user.schemas import PartialUserDto

# ============================================================================
# File-related models
# ============================================================================


class ExternalFile(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    url: str


class NotionHostedFile(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    url: str
    expiry_time: str


class FileUploadFile(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str


class FileData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    caption: list[RichText] = Field(default_factory=list)
    type: FileType
    external: ExternalFile | None = None
    file: NotionHostedFile | None = None
    file_upload: FileUploadFile | None = None
    name: str | None = None


# ============================================================================
# Base Block
# ============================================================================


class BaseBlock(BaseModel):
    id: str
    parent: Parent | None = None
    type: BlockType
    created_time: str
    last_edited_time: str
    created_by: PartialUserDto
    last_edited_by: PartialUserDto
    archived: bool = False
    in_trash: bool = False
    has_children: bool = False


# ============================================================================
# Audio Block
# ============================================================================


class AudioData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    caption: list[RichText] = Field(default_factory=list)
    type: FileType
    external: ExternalFile | None = None
    file: NotionHostedFile | None = None
    file_upload: FileUploadFile | None = None
    name: str | None = None


class AudioBlock(BaseBlock):
    type: Literal[BlockType.AUDIO] = BlockType.AUDIO
    audio: AudioData


class CreateAudioBlock(BaseModel):
    type: Literal[BlockType.AUDIO] = BlockType.AUDIO
    audio: AudioData


# ============================================================================
# Bookmark Block
# ============================================================================


class BookmarkData(BaseModel):
    caption: list[RichText] = Field(default_factory=list)
    url: str


class BookmarkBlock(BaseBlock):
    type: Literal[BlockType.BOOKMARK] = BlockType.BOOKMARK
    bookmark: BookmarkData


class CreateBookmarkBlock(BaseModel):
    type: Literal[BlockType.BOOKMARK] = BlockType.BOOKMARK
    bookmark: BookmarkData


# ============================================================================
# Breadcrumb Block
# ============================================================================


class BreadcrumbData(BaseModel):
    pass


class BreadcrumbBlock(BaseBlock):
    type: Literal[BlockType.BREADCRUMB] = BlockType.BREADCRUMB
    breadcrumb: BreadcrumbData


class CreateBreadcrumbBlock(BaseModel):
    type: Literal[BlockType.BREADCRUMB] = BlockType.BREADCRUMB
    breadcrumb: BreadcrumbData


# ============================================================================
# Bulleted List Item Block
# ============================================================================


class BulletedListItemData(BaseModel):
    rich_text: list[RichText]
    color: BlockColor = BlockColor.DEFAULT


class BulletedListItemBlock(BaseBlock):
    type: Literal[BlockType.BULLETED_LIST_ITEM] = BlockType.BULLETED_LIST_ITEM
    bulleted_list_item: BulletedListItemData


class CreateBulletedListItemBlock(BaseModel):
    type: Literal[BlockType.BULLETED_LIST_ITEM] = BlockType.BULLETED_LIST_ITEM
    bulleted_list_item: BulletedListItemData


# ============================================================================
# Callout Block
# ============================================================================


class CalloutData(BaseModel):
    rich_text: list[RichText]
    color: BlockColor = BlockColor.DEFAULT
    icon: Icon | None = None
    children: list[Block] | None = None


class CalloutBlock(BaseBlock):
    type: Literal[BlockType.CALLOUT] = BlockType.CALLOUT
    callout: CalloutData


class CreateCalloutBlock(BaseModel):
    type: Literal[BlockType.CALLOUT] = BlockType.CALLOUT
    callout: CalloutData


# ============================================================================
# Child Page Block
# ============================================================================


class ChildPageData(BaseModel):
    title: str


class ChildPageBlock(BaseBlock):
    type: Literal[BlockType.CHILD_PAGE] = BlockType.CHILD_PAGE
    child_page: ChildPageData


class CreateChildPageBlock(BaseModel):
    type: Literal[BlockType.CHILD_PAGE] = BlockType.CHILD_PAGE
    child_page: ChildPageData


# ============================================================================
# Child Database Block
# ============================================================================


class ChildDatabaseData(BaseModel):
    title: str


class ChildDatabaseBlock(BaseBlock):
    type: Literal[BlockType.CHILD_DATABASE] = BlockType.CHILD_DATABASE
    child_database: ChildDatabaseData


class CreateChildDatabaseBlock(BaseModel):
    type: Literal[BlockType.CHILD_DATABASE] = BlockType.CHILD_DATABASE
    child_database: ChildDatabaseData


# ============================================================================
# Code Block
# ============================================================================


class CodeData(BaseModel):
    caption: list[RichText] = Field(default_factory=list)
    rich_text: list[RichText]
    language: CodeLanguage = CodeLanguage.PLAIN_TEXT

    model_config = ConfigDict(arbitrary_types_allowed=True)


class CodeBlock(BaseBlock):
    type: Literal[BlockType.CODE] = BlockType.CODE
    code: CodeData


class CreateCodeBlock(BaseModel):
    type: Literal[BlockType.CODE] = BlockType.CODE
    code: CodeData


# ============================================================================
# Column and Column List Blocks
# ============================================================================


class ColumnData(BaseModel):
    width_ratio: float | None = None
    children: list[BlockCreatePayload] = Field(default_factory=list)


class ColumnBlock(BaseBlock):
    type: Literal[BlockType.COLUMN] = BlockType.COLUMN
    column: ColumnData


class CreateColumnBlock(BaseModel):
    type: Literal[BlockType.COLUMN] = BlockType.COLUMN
    column: ColumnData


class ColumnListData(BaseModel):
    children: list[CreateColumnBlock] = Field(default_factory=list)


class ColumnListBlock(BaseBlock):
    type: Literal[BlockType.COLUMN_LIST] = BlockType.COLUMN_LIST
    column_list: ColumnListData


class CreateColumnListBlock(BaseModel):
    type: Literal[BlockType.COLUMN_LIST] = BlockType.COLUMN_LIST
    column_list: ColumnListData


# ============================================================================
# Divider Block
# ============================================================================


class DividerData(BaseModel):
    pass


class DividerBlock(BaseBlock):
    type: Literal[BlockType.DIVIDER] = BlockType.DIVIDER
    divider: DividerData


class CreateDividerBlock(BaseModel):
    type: Literal[BlockType.DIVIDER] = BlockType.DIVIDER
    divider: DividerData


# ============================================================================
# Embed Block
# ============================================================================


class EmbedData(BaseModel):
    url: str
    caption: list[RichText] = Field(default_factory=list)


class EmbedBlock(BaseBlock):
    type: Literal[BlockType.EMBED] = BlockType.EMBED
    embed: EmbedData


class CreateEmbedBlock(BaseModel):
    type: Literal[BlockType.EMBED] = BlockType.EMBED
    embed: EmbedData


# ============================================================================
# Equation Block
# ============================================================================


class EquationData(BaseModel):
    expression: str


class EquationBlock(BaseBlock):
    type: Literal[BlockType.EQUATION] = BlockType.EQUATION
    equation: EquationData


class CreateEquationBlock(BaseModel):
    type: Literal[BlockType.EQUATION] = BlockType.EQUATION
    equation: EquationData


# ============================================================================
# File Block
# ============================================================================


class FileBlock(BaseBlock):
    type: Literal[BlockType.FILE] = BlockType.FILE
    file: FileData


class CreateFileBlock(BaseModel):
    type: Literal[BlockType.FILE] = BlockType.FILE
    file: FileData


# ============================================================================
# Heading Blocks
# ============================================================================


class HeadingData(BaseModel):
    rich_text: list[RichText]
    color: BlockColor = BlockColor.DEFAULT
    is_toggleable: bool = False
    children: list[Block] | None = None


class Heading1Block(BaseBlock):
    type: Literal[BlockType.HEADING_1] = BlockType.HEADING_1
    heading_1: HeadingData


class Heading2Block(BaseBlock):
    type: Literal[BlockType.HEADING_2] = BlockType.HEADING_2
    heading_2: HeadingData


class Heading3Block(BaseBlock):
    type: Literal[BlockType.HEADING_3] = BlockType.HEADING_3
    heading_3: HeadingData


class CreateHeading1Block(BaseModel):
    type: Literal[BlockType.HEADING_1] = BlockType.HEADING_1
    heading_1: HeadingData


class CreateHeading2Block(BaseModel):
    type: Literal[BlockType.HEADING_2] = BlockType.HEADING_2
    heading_2: HeadingData


class CreateHeading3Block(BaseModel):
    type: Literal[BlockType.HEADING_3] = BlockType.HEADING_3
    heading_3: HeadingData


# ============================================================================
# Image Block
# ============================================================================


class ImageData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    caption: list[RichText] = Field(default_factory=list)
    type: FileType
    external: ExternalFile | None = None
    file: NotionHostedFile | None = None
    file_upload: FileUploadFile | None = None
    name: str | None = None


class ImageBlock(BaseBlock):
    type: Literal[BlockType.IMAGE] = BlockType.IMAGE
    image: ImageData


class CreateImageBlock(BaseModel):
    type: Literal[BlockType.IMAGE] = BlockType.IMAGE
    image: ImageData


# ============================================================================
# Numbered List Item Block
# ============================================================================


class NumberedListItemData(BaseModel):
    rich_text: list[RichText]
    color: BlockColor = BlockColor.DEFAULT


class NumberedListItemBlock(BaseBlock):
    type: Literal[BlockType.NUMBERED_LIST_ITEM] = BlockType.NUMBERED_LIST_ITEM
    numbered_list_item: NumberedListItemData


class CreateNumberedListItemBlock(BaseModel):
    type: Literal[BlockType.NUMBERED_LIST_ITEM] = BlockType.NUMBERED_LIST_ITEM
    numbered_list_item: NumberedListItemData


# ============================================================================
# Paragraph Block
# ============================================================================


class ParagraphData(BaseModel):
    rich_text: list[RichText]
    color: BlockColor = BlockColor.DEFAULT


class ParagraphBlock(BaseBlock):
    type: Literal[BlockType.PARAGRAPH] = BlockType.PARAGRAPH
    paragraph: ParagraphData


class CreateParagraphBlock(BaseModel):
    type: Literal[BlockType.PARAGRAPH] = BlockType.PARAGRAPH
    paragraph: ParagraphData


# ============================================================================
# PDF Block
# ============================================================================


class PdfData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    caption: list[RichText] = Field(default_factory=list)
    type: FileType
    external: ExternalFile | None = None
    file: NotionHostedFile | None = None
    file_upload: FileUploadFile | None = None
    name: str | None = None


class PdfBlock(BaseBlock):
    type: Literal[BlockType.PDF] = BlockType.PDF
    pdf: PdfData


class CreatePdfBlock(BaseModel):
    type: Literal[BlockType.PDF] = BlockType.PDF
    pdf: PdfData


# ============================================================================
# Quote Block
# ============================================================================


class QuoteData(BaseModel):
    rich_text: list[RichText]
    color: BlockColor = BlockColor.DEFAULT
    children: list[Block] | None = None


class QuoteBlock(BaseBlock):
    type: Literal[BlockType.QUOTE] = BlockType.QUOTE
    quote: QuoteData


class CreateQuoteBlock(BaseModel):
    type: Literal[BlockType.QUOTE] = BlockType.QUOTE
    quote: QuoteData


# ============================================================================
# Table and Table Row Blocks
# ============================================================================


class TableRowData(BaseModel):
    cells: list[list[RichText]]


class TableRowBlock(BaseBlock):
    type: Literal[BlockType.TABLE_ROW] = BlockType.TABLE_ROW
    table_row: TableRowData


class CreateTableRowBlock(BaseModel):
    type: Literal[BlockType.TABLE_ROW] = BlockType.TABLE_ROW
    table_row: TableRowData


class TableData(BaseModel):
    table_width: int
    has_column_header: bool = False
    has_row_header: bool = False
    children: list[CreateTableRowBlock] = Field(default_factory=list)


class TableBlock(BaseBlock):
    type: Literal[BlockType.TABLE] = BlockType.TABLE
    table: TableData


class CreateTableBlock(BaseModel):
    type: Literal[BlockType.TABLE] = BlockType.TABLE
    table: TableData


# ============================================================================
# Table of Contents Block
# ============================================================================


class TableOfContentsData(BaseModel):
    color: BlockColor = BlockColor.DEFAULT


class TableOfContentsBlock(BaseBlock):
    type: Literal[BlockType.TABLE_OF_CONTENTS] = BlockType.TABLE_OF_CONTENTS
    table_of_contents: TableOfContentsData


class CreateTableOfContentsBlock(BaseModel):
    type: Literal[BlockType.TABLE_OF_CONTENTS] = BlockType.TABLE_OF_CONTENTS
    table_of_contents: TableOfContentsData


# ============================================================================
# To Do Block
# ============================================================================


class ToDoData(BaseModel):
    rich_text: list[RichText]
    checked: bool = False
    color: BlockColor = BlockColor.DEFAULT


class ToDoBlock(BaseBlock):
    type: Literal[BlockType.TO_DO] = BlockType.TO_DO
    to_do: ToDoData


class CreateToDoBlock(BaseModel):
    type: Literal[BlockType.TO_DO] = BlockType.TO_DO
    to_do: ToDoData


# ============================================================================
# Toggle Block
# ============================================================================


class ToggleData(BaseModel):
    rich_text: list[RichText]
    color: BlockColor = BlockColor.DEFAULT
    children: list[Block] | None = None


class ToggleBlock(BaseBlock):
    type: Literal[BlockType.TOGGLE] = BlockType.TOGGLE
    toggle: ToggleData


class CreateToggleBlock(BaseModel):
    type: Literal[BlockType.TOGGLE] = BlockType.TOGGLE
    toggle: ToggleData


# ============================================================================
# Video Block
# ============================================================================


class VideoData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    caption: list[RichText] = Field(default_factory=list)
    type: FileType
    external: ExternalFile | None = None
    file: NotionHostedFile | None = None
    file_upload: FileUploadFile | None = None
    name: str | None = None


class VideoBlock(BaseBlock):
    type: Literal[BlockType.VIDEO] = BlockType.VIDEO
    video: VideoData


class CreateVideoBlock(BaseModel):
    type: Literal[BlockType.VIDEO] = BlockType.VIDEO
    video: VideoData


# ============================================================================
# Block Union Type
# ============================================================================

# TODO: Make a DU out of this here
Block = (
    AudioBlock
    | BookmarkBlock
    | BreadcrumbBlock
    | BulletedListItemBlock
    | CalloutBlock
    | ChildPageBlock
    | ChildDatabaseBlock
    | CodeBlock
    | ColumnListBlock
    | ColumnBlock
    | DividerBlock
    | EmbedBlock
    | EquationBlock
    | FileBlock
    | Heading1Block
    | Heading2Block
    | Heading3Block
    | ImageBlock
    | NumberedListItemBlock
    | ParagraphBlock
    | PdfBlock
    | QuoteBlock
    | TableBlock
    | TableRowBlock
    | TableOfContentsBlock
    | ToDoBlock
    | ToggleBlock
    | VideoBlock
)


# ============================================================================
# Block Response and Request Types
# ============================================================================


class BlockChildrenResponse(BaseModel):
    object: Literal["list"]
    results: list[Block]
    next_cursor: str | None = None
    has_more: bool
    type: Literal["block"]
    block: dict = {}
    request_id: str


# Union type for all create block requests
BlockCreatePayload = (
    CreateAudioBlock
    | CreateBookmarkBlock
    | CreateBreadcrumbBlock
    | CreateBulletedListItemBlock
    | CreateCalloutBlock
    | CreateChildPageBlock
    | CreateChildDatabaseBlock
    | CreateCodeBlock
    | CreateColumnListBlock
    | CreateColumnBlock
    | CreateDividerBlock
    | CreateEmbedBlock
    | CreateEquationBlock
    | CreateFileBlock
    | CreateHeading1Block
    | CreateHeading2Block
    | CreateHeading3Block
    | CreateImageBlock
    | CreateNumberedListItemBlock
    | CreateParagraphBlock
    | CreatePdfBlock
    | CreateQuoteBlock
    | CreateTableBlock
    | CreateTableRowBlock
    | CreateTableOfContentsBlock
    | CreateToDoBlock
    | CreateToggleBlock
    | CreateVideoBlock
)
