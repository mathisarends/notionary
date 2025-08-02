from __future__ import annotations

from typing import Literal, Optional, Union, Any
from pydantic import BaseModel

from notionary.blocks.bookmark import BookmarkBlock, CreateBookmarkBlock
from notionary.blocks.breadcrumbs import BreadcrumbBlock, CreateBreadcrumbBlock
from notionary.blocks.bulleted_list import (
    BulletedListItemBlock,
    CreateBulletedListItemBlock,
)
from notionary.blocks.callout import CalloutBlock, CreateCalloutBlock
from notionary.blocks.child_database import ChildDatabaseBlock, CreateChildDatabaseBlock
from notionary.blocks.child_page import ChildPageBlock, CreateChildPageBlock
from notionary.blocks.code import CodeBlock, CreateCodeBlock
from notionary.blocks.column import (
    ColumnBlock,
    CreateColumnBlock,
    CreateColumnListBlock,
    ColumnListBlock,
)
from notionary.blocks.divider import CreateDividerBlock, DividerBlock
from notionary.blocks.embed import CreateEmbedBlock, EmbedBlock
from notionary.blocks.equation import CreateEquationBlock, EquationBlock
from notionary.blocks.file import CreateFileBlock, FileBlock
from notionary.blocks.heading import (
    CreateHeading1Block,
    CreateHeading2Block,
    CreateHeading3Block,
    Heading1Block,
    Heading2Block,
    Heading3Block,
)
from notionary.blocks.image_block import CreateImageBlock, ImageBlock
from notionary.blocks.numbered_list import (
    CreateNumberedListItemBlock,
    NumberedListItemBlock,
)
from notionary.blocks.paragraph import CreateParagraphBlock, ParagraphBlock
from notionary.blocks.pdf.pdf_models import CreatePdfBlock, PdfBlock
from notionary.blocks.quote import CreateQuoteBlock, QuoteBlock
from notionary.blocks.table import CreateTableOfContentsBlock, TableBlock, TableRowBlock
from notionary.blocks.todo import CreateToDoBlock, ToDoBlock
from notionary.blocks.toggle import CreateToggleBlock, ToggleBlock
from notionary.blocks.video import CreateVideoBlock, VideoBlock


BlockColor = Literal[
    "blue",
    "blue_background",
    "brown",
    "brown_background",
    "default",
    "gray",
    "gray_background",
    "green",
    "green_background",
    "orange",
    "orange_background",
    "yellow",
    "yellow_background",
    "pink",
    "pink_background",
    "purple",
    "purple_background",
    "red",
    "red_background",
    "default_background",
]

BlockType = Literal[
    "bookmark",
    "breadcrumb",
    "bulleted_list_item",
    "callout",
    "child_database",
    "child_page",
    "column",
    "column_list",
    "code",
    "divider",
    "embed",
    "equation",
    "file",
    "heading_1",
    "heading_2",
    "heading_3",
    "image",
    "link_preview",
    "link_to_page",
    "numbered_list_item",
    "paragraph",
    "pdf",
    "quote",
    "synced_block",
    "table",
    "table_of_contents",
    "table_row",
    "to_do",
    "toggle",
    "unsupported",
    "video",
    "audio",
]

BlockCreateRequest = Union[
    CreateBookmarkBlock,
    CreateBreadcrumbBlock,
    CreateBulletedListItemBlock,
    CreateCalloutBlock,
    CreateChildDatabaseBlock,
    CreateChildPageBlock,
    CreateCodeBlock,
    CreateColumnListBlock,
    CreateColumnBlock,
    CreateDividerBlock,
    CreateEmbedBlock,
    CreateEquationBlock,
    CreateFileBlock,
    CreateHeading1Block,
    CreateHeading2Block,
    CreateHeading3Block,
    CreateImageBlock,
    CreateNumberedListItemBlock,
    CreateParagraphBlock,
    CreatePdfBlock,
    CreateQuoteBlock,
    CreateFileBlock,
    CreateTableOfContentsBlock,
    CreateToDoBlock,
    CreateToggleBlock,
    CreateVideoBlock,
]


class BlockChildrenResponse(BaseModel):
    object: Literal["list"]
    results: list[Block]
    next_cursor: Optional[str] = None
    has_more: bool
    type: Literal["block"]
    block: dict = {}
    request_id: str


class PageParent(BaseModel):
    type: Literal["page_id"]
    page_id: str


class DatabaseParent(BaseModel):
    type: Literal["database_id"]
    database_id: str


class BlockParent(BaseModel):
    type: Literal["block_id"]
    block_id: str


class WorkspaceParent(BaseModel):
    type: Literal["workspace"]
    workspace: bool = True


ParentObject = Union[PageParent, DatabaseParent, BlockParent, WorkspaceParent]


class PartialUser(BaseModel):
    object: Literal["user"]
    id: str


class Block(BaseModel):
    object: Literal["block"]
    id: str
    parent: Optional[ParentObject] = None
    type: BlockType
    created_time: str
    last_edited_time: str
    created_by: PartialUser
    last_edited_by: PartialUser
    archived: bool = False
    in_trash: bool = False
    has_children: bool = False

    children: Optional[list[Block]] = None

    # Block type-specific content (only one will be populated based on type)
    bookmark: Optional[BookmarkBlock] = None
    breadcrumb: Optional[BreadcrumbBlock] = None
    bulleted_list_item: Optional[BulletedListItemBlock] = None
    callout: Optional[CalloutBlock] = None
    child_database: Optional[ChildDatabaseBlock] = None
    child_page: Optional[ChildPageBlock] = None
    code: Optional[CodeBlock] = None
    column_list: Optional[ColumnListBlock] = None
    column: Optional[ColumnBlock] = None
    divider: Optional[DividerBlock] = None
    embed: Optional[EmbedBlock] = None
    equation: Optional[EquationBlock] = None
    file: Optional[FileBlock] = None
    heading_1: Optional[Heading1Block] = None
    heading_2: Optional[Heading2Block] = None
    heading_3: Optional[Heading3Block] = None
    image: Optional[ImageBlock] = None
    numbered_list_item: Optional[NumberedListItemBlock] = None
    paragraph: Optional[ParagraphBlock] = None
    pdf: Optional[PdfBlock] = None
    quote: Optional[QuoteBlock] = None
    table: Optional[TableBlock] = None
    table_row: Optional[TableRowBlock] = None
    to_do: Optional[ToDoBlock] = None
    toggle: Optional[ToggleBlock] = None
    video: Optional[VideoBlock] = None

    def get_block_content(self) -> Optional[Any]:
        """Get the content object for this block based on its type."""
        return getattr(self, self.type, None)
