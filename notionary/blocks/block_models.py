from __future__ import annotations

from typing import Literal, Optional, Union, Any, TYPE_CHECKING
from pydantic import BaseModel

if TYPE_CHECKING:
    from notionary.blocks.bookmark import BookmarkBlock, CreateBookmarkBlock
    from notionary.blocks.breadcrumbs import BreadcrumbBlock, CreateBreadcrumbBlock
    from notionary.blocks.bulleted_list import (
        BulletedListItemBlock,
        CreateBulletedListItemBlock,
    )
    from notionary.blocks.callout import CalloutBlock, CreateCalloutBlock
    from notionary.blocks.child_database import (
        ChildDatabaseBlock,
        CreateChildDatabaseBlock,
    )
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
        HeadingBlock,
    )
    from notionary.blocks.image_block import CreateImageBlock, ImageBlock
    from notionary.blocks.numbered_list import (
        CreateNumberedListItemBlock,
        NumberedListItemBlock,
    )
    from notionary.blocks.paragraph import CreateParagraphBlock, ParagraphBlock
    from notionary.blocks.quote import CreateQuoteBlock, QuoteBlock
    from notionary.blocks.table import (
        CreateTableOfContentsBlock,
        TableBlock,
        TableRowBlock,
    )
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
    heading_1: Optional[HeadingBlock] = None
    heading_2: Optional[HeadingBlock] = None
    heading_3: Optional[HeadingBlock] = None
    image: Optional[ImageBlock] = None
    numbered_list_item: Optional[NumberedListItemBlock] = None
    paragraph: Optional[ParagraphBlock] = None
    quote: Optional[QuoteBlock] = None
    table: Optional[TableBlock] = None
    table_row: Optional[TableRowBlock] = None
    to_do: Optional[ToDoBlock] = None
    toggle: Optional[ToggleBlock] = None
    video: Optional[VideoBlock] = None

    def get_block_content(self) -> Optional[Any]:
        """Get the content object for this block based on its type."""
        return getattr(self, self.type, None)


# --- Runtime imports & Pydantic rebuild for forward references ---
# These imports ensure that at runtime all Block subclasses are loaded,
# allowing Pydantic v2 to correctly resolve forward references and recursive
# fields (e.g., children: list[Block]). Without these runtime imports,
# Pydantic would raise "model not fully defined" errors during the rebuild.
from notionary.blocks.bookmark import BookmarkBlock
from notionary.blocks.breadcrumbs import BreadcrumbBlock
from notionary.blocks.bulleted_list import BulletedListItemBlock
from notionary.blocks.callout import CalloutBlock
from notionary.blocks.child_database import ChildDatabaseBlock
from notionary.blocks.child_page import ChildPageBlock
from notionary.blocks.code import CodeBlock
from notionary.blocks.column import ColumnBlock, ColumnListBlock
from notionary.blocks.divider import DividerBlock
from notionary.blocks.embed import EmbedBlock
from notionary.blocks.equation import EquationBlock
from notionary.blocks.file import FileBlock
from notionary.blocks.heading import HeadingBlock
from notionary.blocks.image_block import ImageBlock
from notionary.blocks.numbered_list import NumberedListItemBlock
from notionary.blocks.paragraph import ParagraphBlock
from notionary.blocks.quote import QuoteBlock
from notionary.blocks.table import TableBlock, TableRowBlock
from notionary.blocks.todo import ToDoBlock
from notionary.blocks.toggle import ToggleBlock
from notionary.blocks.video import VideoBlock

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
    CreateQuoteBlock,
    CreateFileBlock,
    CreateToDoBlock,
    CreateToggleBlock,
    CreateVideoBlock,
]

BlockCreateResult = Optional[
    Union[
        list[BlockCreateRequest],
        BlockCreateRequest,
    ]
]

# --- Trigger Pydantic field rebuild for recursive models ---
Block.model_rebuild()
BlockChildrenResponse.model_rebuild()
