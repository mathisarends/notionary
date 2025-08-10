from __future__ import annotations
import re

from notionary.blocks.registry.block_registry import BlockRegistry
from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter
from notionary.blocks.table.table_models import CreateTableRowBlock, TableRowBlock
from notionary.page.content.notion_text_length_utils import fix_blocks_content_length
from notionary.page.formatting.child_content_handler import ChildContentHandler
from notionary.page.formatting.code_block_handler import CodeBlockHandler
from notionary.page.formatting.line_handler import (
    LineProcessingContext,
    ParentBlockContext,
)
from notionary.page.formatting.regular_line_handler import RegularLineHandler
from notionary.page.formatting.table_handler import TableHandler

from notionary.blocks.block_models import BlockCreateRequest


class MarkdownToNotionConverter:
    """Converts Markdown text to Notion API block format with unified stack-based processing."""

    def __init__(self, block_registry: BlockRegistry) -> None:
        self._block_registry = block_registry
        self._setup_handler_chain()

    def _setup_handler_chain(self) -> None:
        """Setup the chain of responsibility for line processing."""
        # Create handlers
        code_handler = CodeBlockHandler()
        table_handler = TableHandler()
        child_handler = ChildContentHandler()
        regular_handler = RegularLineHandler()

        # Chain them together
        code_handler.set_next(table_handler).set_next(child_handler).set_next(
            regular_handler
        )

        self._handler_chain = code_handler

    def convert(self, markdown_text: str) -> list[BlockCreateRequest]:
        """Converts Markdown to Notion blocks using stack-based processing."""
        if not markdown_text.strip():
            return []

        all_blocks = self._process_lines(markdown_text)
        return fix_blocks_content_length(all_blocks)

    def _process_lines(self, text: str) -> list[BlockCreateRequest]:
        """Processes lines using the handler chain."""
        lines = text.split("\n")
        result_blocks: list[BlockCreateRequest] = []
        parent_stack: list[ParentBlockContext] = []

        for line in lines:
            if self._is_column_line_end(line):
                continue
            
            context = LineProcessingContext(
                line=line,
                result_blocks=result_blocks,
                parent_stack=parent_stack,
                block_registry=self._block_registry,
            )

            # Process through handler chain
            self._handler_chain.handle(context)

            if context.should_continue:
                continue

        # Finalize any remaining open parents
        self._finalize_remaining_parents(result_blocks, parent_stack)
        return result_blocks

    def _finalize_remaining_parents(
        self,
        result_blocks: list[BlockCreateRequest],
        parent_stack: list[ParentBlockContext],
    ) -> None:
        """Finalize any remaining open parent blocks."""
        while parent_stack:
            context = parent_stack.pop()

            if context.has_children():
                if context.element_type.__name__ == "CodeElement":
                    # Code content
                    code_content = "\n".join(context.child_lines)
                    if code_content:
                        code_rich = [RichTextObject.from_plain_text(code_content)]
                        context.block.code.rich_text = code_rich
                elif context.element_type.__name__ == "TableElement":
                    # Table processing (delegate to TableHandler logic)
                    self._finalize_table_context(context)
                elif context.element_type.__name__ == "ColumnListElement":
                    # Column processing
                    children_text = "\n".join(context.child_lines)
                    children_blocks = self._convert_children_text(children_text)
                    column_children = [
                        block
                        for block in children_blocks
                        if (
                            hasattr(block, "column")
                            and getattr(block, "type", None) == "column"
                        )
                    ]
                    context.block.column_list.children = column_children
                else:
                    # Standard processing
                    children_text = "\n".join(context.child_lines)
                    children_blocks = self._convert_children_text(children_text)
                    self._assign_children(context.block, children_blocks)

            result_blocks.append(context.block)

    def _finalize_table_context(self, context: ParentBlockContext) -> None:
        """Finalize table context (extracted from TableHandler)."""
        table_rows = []
        separator_found = False
        table_row_pattern = re.compile(r"^\s*\|(.+)\|\s*$")

        for line in context.child_lines:
            line = line.strip()
            if not line:
                continue

            if re.match(r"^\s*\|([\s\-:|]+)\|\s*$", line):
                separator_found = True
                continue

            if table_row_pattern.match(line):
                cells = self._parse_table_row(line)
                rich_text_cells = []
                for cell in cells:
                    rich_text = TextInlineFormatter.parse_inline_formatting(cell)
                    if not rich_text:
                        rich_text = [RichTextObject.from_plain_text(cell)]
                    rich_text_cells.append(rich_text)

                table_row = TableRowBlock(cells=rich_text_cells)
                table_rows.append(CreateTableRowBlock(table_row=table_row))

        context.block.table.children = table_rows

        if table_rows and separator_found:
            context.block.table.has_column_header = True

    def _parse_table_row(self, row_text: str) -> list[str]:
        """Convert table row text to cell contents."""
        row_content = row_text.strip()

        if row_content.startswith("|"):
            row_content = row_content[1:]
        if row_content.endswith("|"):
            row_content = row_content[:-1]

        return [cell.strip() for cell in row_content.split("|")]

    def _convert_children_text(self, text: str) -> list[BlockCreateRequest]:
        """Recursively convert children text."""
        if not text.strip():
            return []
        child_converter = MarkdownToNotionConverter(self._block_registry)
        return child_converter._process_lines(text)

    def _assign_children(
        self, parent_block: BlockCreateRequest, children: list[BlockCreateRequest]
    ):
        """Assign children to a parent block."""

        if hasattr(parent_block, "toggle") and hasattr(parent_block.toggle, "children"):
            parent_block.toggle.children = children
            return

        if hasattr(parent_block, "column_list") and hasattr(
            parent_block.column_list, "children"
        ):
            parent_block.column_list.children = children
            return

        if hasattr(parent_block, "column") and hasattr(parent_block.column, "children"):
            parent_block.column.children = children
            return

        if hasattr(parent_block, "heading_1") and hasattr(
            parent_block.heading_1, "children"
        ):
            parent_block.heading_1.children = children
            return

        if hasattr(parent_block, "heading_2") and hasattr(
            parent_block.heading_2, "children"
        ):
            parent_block.heading_2.children = children
            return

        if hasattr(parent_block, "heading_3") and hasattr(
            parent_block.heading_3, "children"
        ):
            parent_block.heading_3.children = children
            return

        if hasattr(parent_block, "children"):
            parent_block.children = children

    def _is_column_line_end(self, line: str) -> bool:
        """Check if a line indicates the end of a column."""
        return line.strip() == ":::"