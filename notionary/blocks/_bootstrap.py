from __future__ import annotations

from typing import Optional, Union

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
        models,
        numbered_list,
        paragraph,
        quote,
        table,
        table_of_contents,
        todo,
        toggle,
        toggleable_heading,
        video,
        child_database,
    )

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
        child_database,
    ):
        ns.update(vars(m))

    # Add missing types that are needed for model rebuilding
    # These are the types that are only defined in TYPE_CHECKING in block_models
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
    from notionary.blocks.divider.divider_models import CreateDividerBlock, DividerBlock
    from notionary.blocks.embed.embed_models import CreateEmbedBlock, EmbedBlock
    from notionary.blocks.equation.equation_models import (
        CreateEquationBlock,
        EquationBlock,
    )
    from notionary.blocks.file.file_element_models import CreateFileBlock, FileBlock
    from notionary.blocks.heading.heading_models import (
        CreateHeading1Block,
        CreateHeading2Block,
        CreateHeading3Block,
        HeadingBlock,
    )
    from notionary.blocks.image_block.image_models import CreateImageBlock
    from notionary.blocks.numbered_list.numbered_list_models import (
        CreateNumberedListItemBlock,
        NumberedListItemBlock,
    )
    from notionary.blocks.paragraph.paragraph_models import (
        CreateParagraphBlock,
        ParagraphBlock,
    )
    from notionary.blocks.pdf.pdf_models import CreatePdfBlock
    from notionary.blocks.quote.quote_models import CreateQuoteBlock, QuoteBlock
    from notionary.blocks.table.table_models import TableBlock, TableRowBlock
    from notionary.blocks.table_of_contents.table_of_contents_models import (
        CreateTableOfContentsBlock,
        TableOfContentsBlock,
    )
    from notionary.blocks.todo.todo_models import CreateToDoBlock, ToDoBlock
    from notionary.blocks.toggle.toggle_models import CreateToggleBlock, ToggleBlock
    from notionary.blocks.types import BlockType
    from notionary.blocks.video.video_element_models import CreateVideoBlock
    from notionary.blocks.child_database.child_database_models import (
        CreateChildDatabaseBlock,
        ChildDatabaseBlock,
    )

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
        CreatePdfBlock,
        CreateChildDatabaseBlock,
    ]

    BlockCreateResult = Optional[BlockCreateRequest]

    # Add all block types to namespace
    ns.update(
        {
            "BlockType": BlockType,
            "BookmarkBlock": BookmarkBlock,
            "CreateBookmarkBlock": CreateBookmarkBlock,
            "BreadcrumbBlock": BreadcrumbBlock,
            "CreateBreadcrumbBlock": CreateBreadcrumbBlock,
            "BulletedListItemBlock": BulletedListItemBlock,
            "CreateBulletedListItemBlock": CreateBulletedListItemBlock,
            "CalloutBlock": CalloutBlock,
            "CreateCalloutBlock": CreateCalloutBlock,
            "ChildPageBlock": ChildPageBlock,
            "CreateChildPageBlock": CreateChildPageBlock,
            "CodeBlock": CodeBlock,
            "CreateCodeBlock": CreateCodeBlock,
            "ColumnBlock": ColumnBlock,
            "ColumnListBlock": ColumnListBlock,
            "CreateColumnBlock": CreateColumnBlock,
            "CreateColumnListBlock": CreateColumnListBlock,
            "DividerBlock": DividerBlock,
            "CreateDividerBlock": CreateDividerBlock,
            "EmbedBlock": EmbedBlock,
            "CreateEmbedBlock": CreateEmbedBlock,
            "EquationBlock": EquationBlock,
            "CreateEquationBlock": CreateEquationBlock,
            "FileBlock": FileBlock,
            "CreateFileBlock": CreateFileBlock,
            "HeadingBlock": HeadingBlock,
            "CreateHeading1Block": CreateHeading1Block,
            "CreateHeading2Block": CreateHeading2Block,
            "CreateHeading3Block": CreateHeading3Block,
            "CreateImageBlock": CreateImageBlock,
            "NumberedListItemBlock": NumberedListItemBlock,
            "CreateNumberedListItemBlock": CreateNumberedListItemBlock,
            "ParagraphBlock": ParagraphBlock,
            "CreateParagraphBlock": CreateParagraphBlock,
            "QuoteBlock": QuoteBlock,
            "CreateQuoteBlock": CreateQuoteBlock,
            "TableBlock": TableBlock,
            "TableRowBlock": TableRowBlock,
            "ToDoBlock": ToDoBlock,
            "CreateToDoBlock": CreateToDoBlock,
            "ToggleBlock": ToggleBlock,
            "CreateToggleBlock": CreateToggleBlock,
            "CreateVideoBlock": CreateVideoBlock,
            "TableOfContentsBlock": TableOfContentsBlock,
            "CreateTableOfContentsBlock": CreateTableOfContentsBlock,
            "ChildDatabaseBlock": ChildDatabaseBlock,
            # Add the Union types
            "BlockCreateRequest": BlockCreateRequest,
            "BlockCreateResult": BlockCreateResult,
        }
    )

    # Now rebuild with complete namespace
    models.Block.model_rebuild(_types_namespace=ns)
    models.BlockChildrenResponse.model_rebuild(_types_namespace=ns)

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
