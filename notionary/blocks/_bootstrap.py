from __future__ import annotations
from typing import Union, Optional


_bootstrapped = False


def bootstrap_blocks() -> None:
    global _bootstrapped
    if _bootstrapped:
        return

    from notionary.blocks import (
        bookmark,
        breadcrumbs,
        bulleted_list,
        callout,
        child_page,
        code,
        column,
        divider,
        embed,
        equation,
        file,
        heading,
        image_block,
        numbered_list,
        paragraph,
        quote,
        table,
        todo,
        toggle,
        video,
        toggleable_heading,
        table_of_contents,
        
    )
    from notionary.blocks import block_models

    # Collect all exports from modules
    ns = {}
    for m in (
        bookmark,
        breadcrumbs,
        bulleted_list,
        callout,
        child_page,
        code,
        column,
        divider,
        embed,
        equation,
        file,
        heading,
        image_block,
        numbered_list,
        paragraph,
        quote,
        table,
        todo,
        toggle,
        video,
        toggleable_heading,
        table_of_contents,
    ):
        ns.update(vars(m))

    # Add missing types that are needed for model rebuilding
    # These are the types that are only defined in TYPE_CHECKING in block_models
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
    from notionary.blocks.block_types import BlockType
    

    # Define the Union types that are needed for model rebuilding
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

    # Add all block types to namespace
    ns.update({
        'BlockType': BlockType,
        'BookmarkBlock': BookmarkBlock,
        'CreateBookmarkBlock': CreateBookmarkBlock,
        'BreadcrumbBlock': BreadcrumbBlock,
        'CreateBreadcrumbBlock': CreateBreadcrumbBlock,
        'BulletedListItemBlock': BulletedListItemBlock,
        'CreateBulletedListItemBlock': CreateBulletedListItemBlock,
        'CalloutBlock': CalloutBlock,
        'CreateCalloutBlock': CreateCalloutBlock,
        'ChildPageBlock': ChildPageBlock,
        'CreateChildPageBlock': CreateChildPageBlock,
        'CodeBlock': CodeBlock,
        'CreateCodeBlock': CreateCodeBlock,
        'ColumnBlock': ColumnBlock,
        'ColumnListBlock': ColumnListBlock,
        'CreateColumnBlock': CreateColumnBlock,
        'CreateColumnListBlock': CreateColumnListBlock,
        'DividerBlock': DividerBlock,
        'CreateDividerBlock': CreateDividerBlock,
        'EmbedBlock': EmbedBlock,
        'CreateEmbedBlock': CreateEmbedBlock,
        'EquationBlock': EquationBlock,
        'CreateEquationBlock': CreateEquationBlock,
        'FileBlock': FileBlock,
        'CreateFileBlock': CreateFileBlock,
        'HeadingBlock': HeadingBlock,
        'CreateHeading1Block': CreateHeading1Block,
        'CreateHeading2Block': CreateHeading2Block,
        'CreateHeading3Block': CreateHeading3Block,
        'CreateImageBlock': CreateImageBlock,
        'NumberedListItemBlock': NumberedListItemBlock,
        'CreateNumberedListItemBlock': CreateNumberedListItemBlock,
        'ParagraphBlock': ParagraphBlock,
        'CreateParagraphBlock': CreateParagraphBlock,
        'QuoteBlock': QuoteBlock,
        'CreateQuoteBlock': CreateQuoteBlock,
        'TableBlock': TableBlock,
        'TableRowBlock': TableRowBlock,
        'ToDoBlock': ToDoBlock,
        'CreateToDoBlock': CreateToDoBlock,
        'ToggleBlock': ToggleBlock,
        'CreateToggleBlock': CreateToggleBlock,
        'CreateVideoBlock': CreateVideoBlock,
        'TableOfContentsBlock': TableOfContentsBlock,
        'CreateTableOfContentsBlock': CreateTableOfContentsBlock,
        # Add the Union types
        'BlockCreateRequest': BlockCreateRequest,
        'BlockCreateResult': BlockCreateResult,
    })

    # Now rebuild with complete namespace
    block_models.Block.model_rebuild(_types_namespace=ns)
    block_models.BlockChildrenResponse.model_rebuild(_types_namespace=ns)

    # Rebuild all individual block models
    BookmarkBlock.model_rebuild()
    BreadcrumbBlock.model_rebuild()
    BulletedListItemBlock.model_rebuild()
    CalloutBlock.model_rebuild()
    ChildPageBlock.model_rebuild()
    CodeBlock.model_rebuild()
    ColumnBlock.model_rebuild()
    ColumnListBlock.model_rebuild()
    DividerBlock.model_rebuild()
    EmbedBlock.model_rebuild()
    EquationBlock.model_rebuild()
    FileBlock.model_rebuild()
    HeadingBlock.model_rebuild()
    NumberedListItemBlock.model_rebuild()
    ParagraphBlock.model_rebuild()
    QuoteBlock.model_rebuild()
    TableBlock.model_rebuild()
    TableRowBlock.model_rebuild()
    ToDoBlock.model_rebuild()
    ToggleBlock.model_rebuild()
    TableOfContentsBlock.model_rebuild()

    # Rebuild create models
    CreateBookmarkBlock.model_rebuild()
    CreateBreadcrumbBlock.model_rebuild()
    CreateBulletedListItemBlock.model_rebuild()
    CreateCalloutBlock.model_rebuild()
    CreateChildPageBlock.model_rebuild()
    CreateCodeBlock.model_rebuild()
    CreateColumnListBlock.model_rebuild()
    CreateColumnBlock.model_rebuild()
    CreateDividerBlock.model_rebuild()
    CreateEmbedBlock.model_rebuild()
    CreateEquationBlock.model_rebuild()
    CreateFileBlock.model_rebuild()
    CreateHeading1Block.model_rebuild()
    CreateHeading2Block.model_rebuild()
    CreateHeading3Block.model_rebuild()
    CreateImageBlock.model_rebuild()
    CreateNumberedListItemBlock.model_rebuild()
    CreateParagraphBlock.model_rebuild()
    CreateQuoteBlock.model_rebuild()
    CreateToDoBlock.model_rebuild()
    CreateToggleBlock.model_rebuild()
    CreateVideoBlock.model_rebuild()
    CreateTableOfContentsBlock.model_rebuild()

    _bootstrapped = True