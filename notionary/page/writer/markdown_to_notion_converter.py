from notionary.blocks.block_types import BlockType
from notionary.blocks.registry.block_registry import BlockRegistry
from notionary.page.notion_text_length_utils import fix_blocks_content_length
from notionary.page.writer.code_block_handler import CodeBlockHandler
from notionary.page.writer.column_handler import ColumnHandler
from notionary.page.writer.column_list_handler import ColumnListHandler
from notionary.page.writer.context import ParentBlockContext
from notionary.page.writer.toggle_handler import ToggleHandler
from notionary.page.writer.toggleable_heading_handler import (
    ToggleableHeadingHandler,
)
from notionary.page.writer.line_handler import (
    LineProcessingContext,
)
from notionary.page.writer.regular_line_handler import RegularLineHandler
from notionary.page.writer.table_handler import TableHandler

from notionary.blocks.block_models import BlockCreateRequest


class MarkdownToNotionConverter:
    """Converts Markdown text to Notion API block format with unified stack-based processing."""

    def __init__(self, block_registry: BlockRegistry) -> None:
        self._block_registry = block_registry
        self._setup_handler_chain()

    def _setup_handler_chain(self) -> None:
        code_handler = CodeBlockHandler()
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

        self._finalize_remaining_parents(result_blocks, parent_stack)
        return result_blocks

    def _finalize_remaining_parents(
        self,
        result_blocks: list[BlockCreateRequest],
        parent_stack: list[ParentBlockContext],
    ) -> None:
        """Finalize any remaining open parent blocks with unified logic."""
        while parent_stack:
            context = parent_stack.pop()

            if context.has_children():
                children_text = "\n".join(context.child_lines)
                children_blocks = self._convert_children_text(children_text)
                self._assign_children(context.block, children_blocks)

            result_blocks.append(context.block)

    def _convert_children_text(self, text: str) -> list[BlockCreateRequest]:
        if not text.strip():
            return []
        child_converter = MarkdownToNotionConverter(self._block_registry)
        return child_converter._process_lines(text)

    def _assign_children(
        self, parent_block: BlockCreateRequest, children: list[BlockCreateRequest]
    ):
        """Assign children to a parent block using BlockType."""
        block_type = parent_block.type

        if block_type == BlockType.TOGGLE:
            parent_block.toggle.children = children
        elif block_type == BlockType.COLUMN_LIST:
            parent_block.column_list.children = children
        elif block_type == BlockType.COLUMN:
            parent_block.column.children = children
        elif block_type == BlockType.HEADING_1:
            parent_block.heading_1.children = children
        elif block_type == BlockType.HEADING_2:
            parent_block.heading_2.children = children
        elif block_type == BlockType.HEADING_3:
            parent_block.heading_3.children = children
