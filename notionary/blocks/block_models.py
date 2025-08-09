from __future__ import annotations

from typing import Optional, Union, Any, Literal, TYPE_CHECKING
from pydantic import BaseModel
from notionary.blocks.block_types import BlockType

if TYPE_CHECKING:
    from notionary.blocks.bookmark import BookmarkBlock, CreateBookmarkBlock
    from notionary.blocks.breadcrumbs import BreadcrumbBlock, CreateBreadcrumbBlock
    from notionary.blocks.bulleted_list import (
        BulletedListItemBlock,
        CreateBulletedListItemBlock,
    )
    from notionary.blocks.callout import CalloutBlock, CreateCalloutBlock
    from notionary.blocks.child_page import ChildPageBlock, CreateChildPageBlock
    from notionary.blocks.code import CodeBlock, CreateCodeBlock
    from notionary.blocks.column import (
        ColumnBlock,
        ColumnListBlock,
        CreateColumnBlock,
        CreateColumnListBlock,
    )
    from notionary.blocks.divider import DividerBlock, CreateDividerBlock
    from notionary.blocks.embed import EmbedBlock, CreateEmbedBlock
    from notionary.blocks.equation import EquationBlock, CreateEquationBlock
    from notionary.blocks.file import FileBlock, CreateFileBlock
    from notionary.blocks.heading import (
        HeadingBlock,
        CreateHeading1Block,
        CreateHeading2Block,
        CreateHeading3Block,
    )
    from notionary.blocks.image_block import CreateImageBlock
    from notionary.blocks.numbered_list import (
        NumberedListItemBlock,
        CreateNumberedListItemBlock,
    )
    from notionary.blocks.paragraph import ParagraphBlock, CreateParagraphBlock
    from notionary.blocks.quote import QuoteBlock, CreateQuoteBlock
    from notionary.blocks.table import TableBlock, TableRowBlock
    from notionary.blocks.todo import ToDoBlock, CreateToDoBlock
    from notionary.blocks.toggle import ToggleBlock, CreateToggleBlock
    from notionary.blocks.video import CreateVideoBlock
    from notionary.blocks.table_of_contents.table_of_contents_models import (
        TableOfContentsBlock,
        CreateTableOfContentsBlock,
    )


class BlockChildrenResponse(BaseModel):
    object: Literal["list"]
    results: list["Block"]
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
    audio: Optional[FileBlock] = None
    bookmark: Optional[BookmarkBlock] = None
    breadcrumb: Optional[BreadcrumbBlock] = None
    bulleted_list_item: Optional[BulletedListItemBlock] = None
    callout: Optional[CalloutBlock] = None
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
    image: Optional[FileBlock] = None
    numbered_list_item: Optional[NumberedListItemBlock] = None
    paragraph: Optional[ParagraphBlock] = None
    quote: Optional[QuoteBlock] = None
    table: Optional[TableBlock] = None
    table_row: Optional[TableRowBlock] = None
    to_do: Optional[ToDoBlock] = None
    toggle: Optional[ToggleBlock] = None
    video: Optional[FileBlock] = None
    table_of_contents: Optional[TableOfContentsBlock] = None

    def get_block_content(self) -> Optional[Any]:
        """Get the content object for this block based on its type."""
        return getattr(self, self.type, None)


if TYPE_CHECKING:
    BlockCreateRequest = Union[
        CreateBookmarkBlock,
        CreateBreadcrumbBlock,
        CreateBulletedListItemBlock,
        CreateCalloutBlock,
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
        CreateToDoBlock,
        CreateToggleBlock,
        CreateVideoBlock,
        CreateTableOfContentsBlock,
    ]
    BlockCreateResult = Optional[Union[list[BlockCreateRequest], BlockCreateRequest]]
else:
    BlockCreateRequest = Any
    BlockCreateResult = Any
