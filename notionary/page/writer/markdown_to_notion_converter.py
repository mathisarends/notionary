from typing import cast

from notionary.blocks.models import BlockCreateRequest
from notionary.blocks.paragraph.paragraph_models import (CreateParagraphBlock,
                                                         ParagraphBlock)
from notionary.blocks.registry.block_registry import BlockRegistry
from notionary.blocks.types import BlockType
from notionary.page.notion_text_length_utils import fix_blocks_content_length
from notionary.page.writer.handler import (CodeHandler, ColumnHandler,
                                           ColumnListHandler,
                                           LineProcessingContext,
                                           ParentBlockContext,
                                           RegularLineHandler, TableHandler,
                                           ToggleableHeadingHandler,
                                           ToggleHandler)


class MarkdownToNotionConverter:
    """Converts Markdown text to Notion API block format with unified stack-based processing."""

    BLOCKS_NEEDING_EMPTY_PARAGRAPH = {"divider", "file", "image", "pdf", "video"}

    def __init__(self, block_registry: BlockRegistry) -> None:
        self._block_registry = block_registry
        self._setup_handler_chain()

    def _setup_handler_chain(self) -> None:
        code_handler = CodeHandler()
        table_handler = TableHandler()
        column_list_handler = ColumnListHandler()
        column_handler = ColumnHandler()
        toggle_handler = ToggleHandler()
        toggleable_heading_handler = ToggleableHeadingHandler()
        regular_handler = RegularLineHandler()

        # register more specific elements first
        code_handler.set_next(table_handler).set_next(column_list_handler).set_next(
            column_handler
        ).set_next(toggleable_heading_handler).set_next(toggle_handler).set_next(
            regular_handler
        )

        self._handler_chain = code_handler

    def convert(self, markdown_text: str) -> list[BlockCreateRequest]:
        if not markdown_text.strip():
            return []

        all_blocks = self._process_lines(markdown_text)
        all_blocks = self._add_empty_paragraphs_for_media_blocks(all_blocks)
        return fix_blocks_content_length(all_blocks)

    def _process_lines(self, text: str) -> list[BlockCreateRequest]:
        lines = text.split("\n")
        result_blocks: list[BlockCreateRequest] = []
        parent_stack: list[ParentBlockContext] = []

        i = 0
        while i < len(lines):
            line = lines[i]

            context = LineProcessingContext(
                line=line,
                result_blocks=result_blocks,
                parent_stack=parent_stack,
                block_registry=self._block_registry,
                all_lines=lines,
                current_line_index=i,
                lines_consumed=0,
            )

            self._handler_chain.handle(context)

            # Skip consumed lines
            i += 1 + context.lines_consumed

            if context.should_continue:
                continue

        return result_blocks

    def _add_empty_paragraphs_for_media_blocks(
        self, blocks: list[BlockCreateRequest]
    ) -> list[BlockCreateRequest]:
        """Add empty paragraphs before configured block types."""
        if not blocks:
            return blocks

        result = []

        for i, block in enumerate(blocks):
            block_type = block.type

            if (
                block_type in self.BLOCKS_NEEDING_EMPTY_PARAGRAPH
                and i > 0
                and not self._is_empty_paragraph(result[-1] if result else None)
            ):

                # Create empty paragraph block inline
                empty_paragraph = CreateParagraphBlock(
                    paragraph=ParagraphBlock(rich_text=[])
                )
                result.append(empty_paragraph)

            result.append(block)

        return result

    def _is_empty_paragraph(self, block: BlockCreateRequest | None) -> bool:
        if not block or block.type != BlockType.PARAGRAPH:
            return False
        if not isinstance(block, CreateParagraphBlock):
            return False  # Safety: nur Paragraph-Create-Block hat .paragraph

        para_block = cast(CreateParagraphBlock, block)
        paragraph: ParagraphBlock | None = para_block.paragraph
        if not paragraph:
            return False

        return not paragraph.rich_text or len(paragraph.rich_text) == 0
