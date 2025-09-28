from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from pydantic import BaseModel

from notionary.blocks.types import BlockType
from notionary.shared.models.parent_models import Parent
from notionary.shared.models.user_models import NotionUser

if TYPE_CHECKING:
    from notionary.blocks.bookmark import BookmarkBlock, CreateBookmarkBlock
    from notionary.blocks.breadcrumbs import BreadcrumbBlock, CreateBreadcrumbBlock
    from notionary.blocks.bulleted_list import (
        BulletedListItemBlock,
        CreateBulletedListItemBlock,
    )
    from notionary.blocks.callout import CalloutBlock, CreateCalloutBlock
    from notionary.blocks.child_database import ChildDatabaseBlock
    from notionary.blocks.child_page import ChildPageBlock, CreateChildPageBlock
    from notionary.blocks.code import CodeBlock, CreateCodeBlock
    from notionary.blocks.column import (
        ColumnBlock,
        ColumnListBlock,
        CreateColumnBlock,
        CreateColumnListBlock,
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
    from notionary.blocks.image_block import CreateImageBlock
    from notionary.blocks.numbered_list import (
        CreateNumberedListItemBlock,
        NumberedListItemBlock,
    )
    from notionary.blocks.paragraph import CreateParagraphBlock, ParagraphBlock
    from notionary.blocks.pdf import CreatePdfBlock
    from notionary.blocks.quote import CreateQuoteBlock, QuoteBlock
    from notionary.blocks.table import CreateTableBlock, TableBlock, TableRowBlock
    from notionary.blocks.table_of_contents import (
        CreateTableOfContentsBlock,
        TableOfContentsBlock,
    )
    from notionary.blocks.todo import CreateToDoBlock, ToDoBlock
    from notionary.blocks.toggle import CreateToggleBlock, ToggleBlock
    from notionary.blocks.video import CreateVideoBlock


class BlockChildrenResponse(BaseModel):
    object: Literal["list"]
    results: list[Block]
    next_cursor: str | None = None
    has_more: bool
    type: Literal["block"]
    block: dict = {}
    request_id: str


class Block(BaseModel):
    object: Literal["block"]
    id: str
    parent: Parent | None = None
    type: BlockType
    created_time: str
    last_edited_time: str
    created_by: NotionUser
    last_edited_by: NotionUser
    archived: bool = False
    in_trash: bool = False
    has_children: bool = False

    children: list[Block] | None = None

    # Block type-specific content (only one will be populated based on type)
    audio: FileBlock | None = None
    bookmark: BookmarkBlock | None = None
    breadcrumb: BreadcrumbBlock | None = None
    bulleted_list_item: BulletedListItemBlock | None = None
    callout: CalloutBlock | None = None
    child_page: ChildPageBlock | None = None
    code: CodeBlock | None = None
    column_list: ColumnListBlock | None = None
    column: ColumnBlock | None = None
    divider: DividerBlock | None = None
    embed: EmbedBlock | None = None
    equation: EquationBlock | None = None
    file: FileBlock | None = None
    heading_1: HeadingBlock | None = None
    heading_2: HeadingBlock | None = None
    heading_3: HeadingBlock | None = None
    image: FileBlock | None = None
    numbered_list_item: NumberedListItemBlock | None = None
    paragraph: ParagraphBlock | None = None
    quote: QuoteBlock | None = None
    table: TableBlock | None = None
    table_row: TableRowBlock | None = None
    to_do: ToDoBlock | None = None
    toggle: ToggleBlock | None = None
    video: FileBlock | None = None
    pdf: FileBlock | None = None
    table_of_contents: TableOfContentsBlock | None = None
    child_database: ChildDatabaseBlock | None = None


if TYPE_CHECKING:
    BlockCreateRequest = (
        CreateBookmarkBlock
        | CreateBreadcrumbBlock
        | CreateBulletedListItemBlock
        | CreateCalloutBlock
        | CreateChildPageBlock
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
        | CreateQuoteBlock
        | CreateToDoBlock
        | CreateToggleBlock
        | CreateVideoBlock
        | CreateTableOfContentsBlock
        | CreatePdfBlock
        | CreateTableBlock
    )
    BlockCreateResult = BlockCreateRequest
else:
    # at runtime there are no typings anyway
    BlockCreateRequest = Any
    BlockCreateResult = Any
