from __future__ import annotations

from typing import Optional, Union, Any, Literal, TYPE_CHECKING
from pydantic import BaseModel
from notionary.blocks.block_types import BlockType

if TYPE_CHECKING:
    from notionary.blocks.bookmark.bookmark_models import (
        BookmarkBlock,
        CreateBookmarkBlock,
    )
    from notionary.blocks.breadcrumbs.breadcrumb_models import (
        BreadcrumbBlock,
        CreateBreadcrumbBlock,
    )
    from notionary.blocks.bulleted_list.bulleted_list_models import (
        BulletedListItemBlock,
        CreateBulletedListItemBlock,
    )
    from notionary.blocks.callout.callout_models import CalloutBlock, CreateCalloutBlock
    from notionary.blocks.child_page.child_page_models import (
        ChildPageBlock,
        CreateChildPageBlock,
    )
    from notionary.blocks.code.code_models import CodeBlock, CreateCodeBlock
    from notionary.blocks.column.column_models import (
        ColumnBlock,
        ColumnListBlock,
        CreateColumnBlock,
        CreateColumnListBlock,
    )
    from notionary.blocks.divider.divider_models import DividerBlock, CreateDividerBlock
    from notionary.blocks.embed.embed_models import EmbedBlock, CreateEmbedBlock
    from notionary.blocks.equation.equation_models import (
        EquationBlock,
        CreateEquationBlock,
    )
    from notionary.blocks.file.file_element_models import FileBlock, CreateFileBlock
    from notionary.blocks.heading.heading_models import (
        HeadingBlock,
        CreateHeading1Block,
        CreateHeading2Block,
        CreateHeading3Block,
    )
    from notionary.blocks.image_block.image_models import CreateImageBlock
    from notionary.blocks.numbered_list.numbered_list_models import (
        NumberedListItemBlock,
        CreateNumberedListItemBlock,
    )
    from notionary.blocks.paragraph.paragraph_models import (
        ParagraphBlock,
        CreateParagraphBlock,
    )
    from notionary.blocks.quote.quote_models import QuoteBlock, CreateQuoteBlock
    from notionary.blocks.table.table_models import TableBlock, TableRowBlock
    from notionary.blocks.todo.todo_models import ToDoBlock, CreateToDoBlock
    from notionary.blocks.toggle.toggle_models import ToggleBlock, CreateToggleBlock
    from notionary.blocks.video.video_element_models import CreateVideoBlock
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
    # at runtime there are no typings anyway
    BlockCreateRequest = Any
    BlockCreateResult = Any
