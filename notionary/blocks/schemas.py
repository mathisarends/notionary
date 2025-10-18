from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from notionary.blocks.enums import BlockColor, BlockType, CodingLanguage, FileType
from notionary.blocks.rich_text.models import RichText
from notionary.shared.models.icon import Icon
from notionary.shared.models.parent import Parent
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
    children: list[Block] | None = None


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


class BaseBulletedListItemData(BaseModel):
    rich_text: list[RichText]
    color: BlockColor = BlockColor.DEFAULT


class BulletedListItemData(BaseBulletedListItemData):
    children: list[Block] | None = None


class BulletedListItemBlock(BaseBlock):
    type: Literal[BlockType.BULLETED_LIST_ITEM] = BlockType.BULLETED_LIST_ITEM
    bulleted_list_item: BulletedListItemData


class CreateBulletedListItemData(BaseBulletedListItemData):
    children: list[BlockCreatePayload] | None = None


class CreateBulletedListItemBlock(BaseModel):
    type: Literal[BlockType.BULLETED_LIST_ITEM] = BlockType.BULLETED_LIST_ITEM
    bulleted_list_item: CreateBulletedListItemData


# ============================================================================
# Callout Block
# ============================================================================


class BaseCalloutData(BaseModel):
    rich_text: list[RichText]
    color: BlockColor = BlockColor.DEFAULT
    icon: Icon | None = None


class CalloutData(BaseCalloutData):
    children: list[Block] | None = None


class CalloutBlock(BaseBlock):
    type: Literal[BlockType.CALLOUT] = BlockType.CALLOUT
    callout: CalloutData


class CreateCalloutData(BaseCalloutData):
    children: list[BlockCreatePayload] | None = None


class CreateCalloutBlock(BaseModel):
    type: Literal[BlockType.CALLOUT] = BlockType.CALLOUT
    callout: CreateCalloutData


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
    language: CodingLanguage = CodingLanguage.PLAIN_TEXT

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


class BaseColumnData(BaseModel):
    width_ratio: float | None = None


class ColumnData(BaseColumnData):
    children: list[Block] = Field(default_factory=list)


class ColumnBlock(BaseBlock):
    type: Literal[BlockType.COLUMN] = BlockType.COLUMN
    column: ColumnData


class CreateColumnData(BaseColumnData):
    children: list[BlockCreatePayload] = Field(default_factory=list)


class CreateColumnBlock(BaseModel):
    type: Literal[BlockType.COLUMN] = BlockType.COLUMN
    column: CreateColumnData


class ColumnListData(BaseModel):
    children: list[ColumnBlock] = Field(default_factory=list)


class ColumnListBlock(BaseBlock):
    type: Literal[BlockType.COLUMN_LIST] = BlockType.COLUMN_LIST
    column_list: ColumnListData


class CreateColumnListData(BaseModel):
    children: list[CreateColumnBlock] = Field(default_factory=list)


class CreateColumnListBlock(BaseModel):
    type: Literal[BlockType.COLUMN_LIST] = BlockType.COLUMN_LIST
    column_list: CreateColumnListData


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


class BaseHeadingData(BaseModel):
    rich_text: list[RichText]
    color: BlockColor = BlockColor.DEFAULT
    is_toggleable: bool = False


class HeadingData(BaseHeadingData):
    children: list[Block] | None = None


class CreateHeadingData(BaseHeadingData):
    children: list[BlockCreatePayload] | None = None


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
    heading_1: CreateHeadingData


class CreateHeading2Block(BaseModel):
    type: Literal[BlockType.HEADING_2] = BlockType.HEADING_2
    heading_2: CreateHeadingData


class CreateHeading3Block(BaseModel):
    type: Literal[BlockType.HEADING_3] = BlockType.HEADING_3
    heading_3: CreateHeadingData


CreateHeadingBlock = CreateHeading1Block | CreateHeading2Block | CreateHeading3Block

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


class BaseNumberedListItemData(BaseModel):
    rich_text: list[RichText]
    color: BlockColor = BlockColor.DEFAULT


class NumberedListItemData(BaseNumberedListItemData):
    children: list[Block] | None = None


class NumberedListItemBlock(BaseBlock):
    type: Literal[BlockType.NUMBERED_LIST_ITEM] = BlockType.NUMBERED_LIST_ITEM
    numbered_list_item: NumberedListItemData


class CreateNumberedListItemData(BaseNumberedListItemData):
    children: list[BlockCreatePayload] | None = None


class CreateNumberedListItemBlock(BaseModel):
    type: Literal[BlockType.NUMBERED_LIST_ITEM] = BlockType.NUMBERED_LIST_ITEM
    numbered_list_item: CreateNumberedListItemData


# ============================================================================
# Paragraph Block
# ============================================================================


class BaseParagraphData(BaseModel):
    rich_text: list[RichText]
    color: BlockColor = BlockColor.DEFAULT


class ParagraphData(BaseParagraphData):
    children: list[Block] | None = None


class ParagraphBlock(BaseBlock):
    type: Literal[BlockType.PARAGRAPH] = BlockType.PARAGRAPH
    paragraph: ParagraphData


class CreateParagraphData(BaseParagraphData):
    children: list[BlockCreatePayload] | None = None


class CreateParagraphBlock(BaseModel):
    type: Literal[BlockType.PARAGRAPH] = BlockType.PARAGRAPH
    paragraph: CreateParagraphData


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


class BaseQuoteData(BaseModel):
    rich_text: list[RichText]
    color: BlockColor = BlockColor.DEFAULT


class QuoteData(BaseQuoteData):
    children: list[Block] | None = None


class QuoteBlock(BaseBlock):
    type: Literal[BlockType.QUOTE] = BlockType.QUOTE
    quote: QuoteData


class CreateQuoteData(BaseQuoteData):
    children: list[BlockCreatePayload] | None = None


class CreateQuoteBlock(BaseModel):
    type: Literal[BlockType.QUOTE] = BlockType.QUOTE
    quote: CreateQuoteData


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


class BaseTableData(BaseModel):
    table_width: int
    has_column_header: bool = False
    has_row_header: bool = False


class TableData(BaseTableData):
    children: list[TableRowBlock] = Field(default_factory=list)


class TableBlock(BaseBlock):
    type: Literal[BlockType.TABLE] = BlockType.TABLE
    table: TableData


class CreateTableData(BaseTableData):
    children: list[CreateTableRowBlock] = Field(default_factory=list)


class CreateTableBlock(BaseModel):
    type: Literal[BlockType.TABLE] = BlockType.TABLE
    table: CreateTableData


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


class BaseToDoData(BaseModel):
    rich_text: list[RichText]
    checked: bool = False
    color: BlockColor = BlockColor.DEFAULT


class ToDoData(BaseToDoData):
    children: list[Block] | None = None


class ToDoBlock(BaseBlock):
    type: Literal[BlockType.TO_DO] = BlockType.TO_DO
    to_do: ToDoData


class CreateToDoData(BaseToDoData):
    children: list[BlockCreatePayload] | None = None


class CreateToDoBlock(BaseModel):
    type: Literal[BlockType.TO_DO] = BlockType.TO_DO
    to_do: CreateToDoData


# ============================================================================
# Toggle Block
# ============================================================================


class BaseToggleData(BaseModel):
    rich_text: list[RichText]
    color: BlockColor = BlockColor.DEFAULT


class ToggleData(BaseToggleData):
    children: list[Block] | None = None


class ToggleBlock(BaseBlock):
    type: Literal[BlockType.TOGGLE] = BlockType.TOGGLE
    toggle: ToggleData


class CreateToggleData(BaseToggleData):
    children: list[BlockCreatePayload] | None = None


class CreateToggleBlock(BaseModel):
    type: Literal[BlockType.TOGGLE] = BlockType.TOGGLE
    toggle: CreateToggleData


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

Block = Annotated[
    (
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
    ),
    Field(discriminator="type"),
]


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


BlockCreatePayload = Annotated[
    (
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
    ),
    Field(discriminator="type"),
]
