from __future__ import annotations
import re
from typing import TYPE_CHECKING
from dataclasses import dataclass

from notionary.blocks.registry.block_registry import BlockRegistry
from notionary.blocks.notion_block_element import NotionBlockElement
from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter
from notionary.blocks.table.table_models import CreateTableRowBlock, TableRowBlock
from notionary.page.formatting.block_position import PositionedBlockList
from notionary.page.content.notion_text_length_utils import fix_blocks_content_length

if TYPE_CHECKING:
    from notionary.blocks.block_models import BlockCreateRequest, BlockCreateResult


@dataclass
class ParentBlockContext:
    """Context for a block that expects children."""

    block: BlockCreateRequest
    element_type: NotionBlockElement
    child_prefix: str
    child_lines: list[str]
    start_position: int

    def add_child_line(self, content: str):
        """Adds a child line."""
        self.child_lines.append(content)

    def has_children(self) -> bool:
        """Checks if children have been collected."""
        return len(self.child_lines) > 0


class MarkdownToNotionConverter:
    """Converts Markdown text to Notion API block format with unified stack-based processing."""

    def __init__(self, block_registry: BlockRegistry) -> None:
        self._block_registry = block_registry
        self._parent_stack: list[ParentBlockContext] = []

        # ALL elements that can have children use the "|" prefix
        self._child_prefixes = {
            "ToggleElement": "|",
            "ToggleableHeadingElement": "|",
            "ColumnListElement": "|",
            "ColumnElement": "|",
            "CodeElement": "RAW",  # Code blocks take raw lines without prefix
            "TableElement": "TABLE_ROW",  # Tables collect table row lines
        }

        # Pattern for code block end
        self._code_end_pattern = re.compile(r"^```\s*$")
        # Pattern for caption after code block
        self._caption_pattern = re.compile(r"^(?:Caption|caption):\s*(.+)$")
        # Pattern for table rows (imported from TableElement)
        self._table_row_pattern = re.compile(r"^\s*\|(.+)\|\s*$")

    def convert(self, markdown_text: str) -> list[BlockCreateRequest]:
        """Converts Markdown to Notion blocks using stack-based processing."""
        if not markdown_text.strip():
            return []

        all_blocks = self._process_lines(markdown_text)
        blocks = all_blocks.extract_blocks()
        return fix_blocks_content_length(blocks)

    def _process_lines(self, text: str) -> PositionedBlockList:
        """Processes lines with unified | child support + Code block + Table support."""
        lines = text.split("\n")
        result_blocks = PositionedBlockList()
        current_pos = 0

        for line in lines:
            line_length = len(line) + 1
            line_end = current_pos + line_length - 1

            # Check for code block end
            if self._try_process_code_end(line, result_blocks, current_pos):
                current_pos += line_length
                continue

            # Check for caption after code block
            if self._try_process_caption(line):
                current_pos += line_length
                continue

            # Check if we "fall out" of a table (table end)
            if self._try_process_table_end(line, result_blocks, current_pos):
                # Table was ended, but current line still needs to be processed
                # Therefore NO continue here
                pass

            # Check for child content (with | prefix, RAW for code, TABLE_ROW for tables)
            if self._try_process_as_child(line):
                current_pos += line_length
                continue

            # Finalize open parents before processing new blocks
            self._finalize_open_parents(result_blocks, current_pos)

            if line.strip():
                block_created = self._process_regular_line(
                    line, current_pos, line_end, result_blocks
                )
                if not block_created:
                    self._process_as_paragraph(
                        line, current_pos, line_end, result_blocks
                    )

            current_pos += line_length

        self._finalize_open_parents(result_blocks, current_pos)
        return result_blocks

    def _try_process_table_end(
        self, line: str, result_blocks: PositionedBlockList, current_pos: int
    ) -> bool:
        """Check if we need to end a table (line doesn't match table pattern)."""
        if not self._parent_stack:
            return False

        current_parent = self._parent_stack[-1]
        if current_parent.element_type.__name__ != "TableElement":
            return False

        # If the line does NOT match the table pattern, end the table
        if not self._table_row_pattern.match(line.strip()) and line.strip():
            self._finalize_table(result_blocks, current_pos)
            return True

        return False

    def _finalize_table(self, result_blocks: PositionedBlockList, current_pos: int):
        """Finalize a table and convert child lines to table rows."""
        if not self._parent_stack:
            return

        context = self._parent_stack.pop()

        if context.has_children() and context.element_type.__name__ == "TableElement":
            # Convert child lines to table rows
            table_rows = []
            separator_found = False

            for line in context.child_lines:
                line = line.strip()
                if not line:
                    continue

                # Check for separator line (| ---- | ---- |)
                if re.match(r"^\s*\|([\s\-:|]+)\|\s*$", line):
                    separator_found = True
                    continue

                # Parse table row
                if self._table_row_pattern.match(line):
                    cells = self._parse_table_row(line)
                    # Convert to RichTextObject arrays
                    rich_text_cells = []
                    for cell in cells:
                        # Use TextInlineFormatter for rich text support
                        rich_text = TextInlineFormatter.parse_inline_formatting(cell)
                        if not rich_text:
                            rich_text = [RichTextObject.from_plain_text(cell)]
                        rich_text_cells.append(rich_text)

                    table_row = TableRowBlock(cells=rich_text_cells)
                    table_rows.append(CreateTableRowBlock(table_row=table_row))

            # Set table rows as children
            context.block.table.children = table_rows

            # Ensure has_column_header is set correctly
            if table_rows and separator_found:
                context.block.table.has_column_header = True

        result_blocks.add(context.start_position, current_pos, context.block)

    def _parse_table_row(self, row_text: str) -> list[str]:
        """Convert table row text to cell contents."""
        row_content = row_text.strip()

        if row_content.startswith("|"):
            row_content = row_content[1:]
        if row_content.endswith("|"):
            row_content = row_content[:-1]

        return [cell.strip() for cell in row_content.split("|")]

    def _try_process_code_end(
        self, line: str, result_blocks: PositionedBlockList, current_pos: int
    ) -> bool:
        """Check if line ends a code block (```)."""
        if not self._code_end_pattern.match(line.strip()):
            return False

        if not self._parent_stack:
            return False

        current_parent = self._parent_stack[-1]
        if current_parent.element_type.__name__ != "CodeElement":
            return False

        # Finalize the code block
        context = self._parent_stack.pop()

        if context.has_children():
            # Join code content
            code_content = "\n".join(context.child_lines)
            code_rich = (
                [RichTextObject.from_plain_text(code_content)] if code_content else []
            )
            context.block.code.rich_text = code_rich

        result_blocks.add(context.start_position, current_pos, context.block)
        return True

    def _try_process_caption(self, line: str) -> bool:
        """Check if line is a caption for the last code block."""
        # This method is for future caption support
        # Currently just skip
        match = self._caption_pattern.match(line.strip())
        if match:
            # TODO: Add caption to last code block
            return True
        return False

    def _try_process_as_child(self, line: str) -> bool:
        """Process as child content - EXACTLY like toggles + RAW for code + TABLE_ROW for tables."""
        if not self._parent_stack:
            return False

        current_parent = self._parent_stack[-1]
        child_prefix = current_parent.child_prefix

        # Special handling for code blocks: RAW content (no prefix processing)
        if child_prefix == "RAW":
            current_parent.add_child_line(line)
            return True

        # Special handling for tables: TABLE_ROW content
        if child_prefix == "TABLE_ROW":
            # Check if the line matches the table pattern
            if self._table_row_pattern.match(line.strip()):
                current_parent.add_child_line(line)
                return True
            # If not, end the table (handled in process_lines)
            return False

        # The proven toggle system for other elements
        child_pattern = re.compile(rf"^{re.escape(child_prefix)}\s?(.*?)$")
        match = child_pattern.match(line)

        if match:
            child_content = match.group(1)
            current_parent.add_child_line(child_content)
            return True

        return False

    def _process_regular_line(
        self,
        line: str,
        current_pos: int,
        line_end: int,
        result_blocks: PositionedBlockList,
    ) -> bool:
        """Process a regular line and check for parent blocks."""

        for element in self._block_registry.get_elements():
            if not element.match_markdown(line):
                continue

            result = element.markdown_to_notion(line)
            blocks = self._normalize_to_list(result)

            if not blocks:
                continue

            for block in blocks:
                if not self._can_have_children(block, element):
                    result_blocks.add(current_pos, line_end, block)
                else:
                    child_prefix = self._get_child_prefix(element)

                    context = ParentBlockContext(
                        block=block,
                        element_type=element,
                        child_prefix=child_prefix,
                        child_lines=[],
                        start_position=current_pos,
                    )
                    self._parent_stack.append(context)

            return True

        return False

    def _finalize_open_parents(
        self, result_blocks: PositionedBlockList, current_pos: int
    ):
        """Finalize all open parent blocks - including code blocks and tables."""
        while self._parent_stack:
            context = self._parent_stack.pop()

            if context.has_children():
                if context.element_type.__name__ == "CodeElement":
                    # Assign code content directly
                    code_content = "\n".join(context.child_lines)
                    if code_content:
                        code_rich = [RichTextObject.from_plain_text(code_content)]
                        context.block.code.rich_text = code_rich
                elif context.element_type.__name__ == "TableElement":
                    # Process table rows
                    table_rows = []
                    separator_found = False

                    for line in context.child_lines:
                        line = line.strip()
                        if not line:
                            continue

                        # Check for separator line (| ---- | ---- |)
                        if re.match(r"^\s*\|([\s\-:|]+)\|\s*$", line):
                            separator_found = True
                            continue

                        # Parse table row
                        if self._table_row_pattern.match(line):
                            cells = self._parse_table_row(line)
                            # Convert to RichTextObject arrays
                            rich_text_cells = []
                            for cell in cells:
                                # Use TextInlineFormatter for rich text support
                                rich_text = TextInlineFormatter.parse_inline_formatting(
                                    cell
                                )
                                if not rich_text:
                                    rich_text = [RichTextObject.from_plain_text(cell)]
                                rich_text_cells.append(rich_text)

                            table_row = TableRowBlock(cells=rich_text_cells)
                            table_rows.append(CreateTableRowBlock(table_row=table_row))

                    # Set table rows as children
                    context.block.table.children = table_rows

                    # Ensure has_column_header is set correctly
                    if table_rows and separator_found:
                        context.block.table.has_column_header = True
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
                    # Standard processing for other elements
                    children_text = "\n".join(context.child_lines)
                    children_blocks = self._convert_children_text(children_text)
                    self._assign_children(context.block, children_blocks)

            result_blocks.add(context.start_position, current_pos, context.block)

    def _process_as_paragraph(
        self,
        line: str,
        current_pos: int,
        line_end: int,
        result_blocks: PositionedBlockList,
    ):
        """Process a line as a paragraph."""
        result = self._block_registry.markdown_to_notion(line)
        blocks = self._normalize_to_list(result)
        for block in blocks:
            result_blocks.add(current_pos, line_end, block)

    def _can_have_children(
        self, block: BlockCreateRequest, element: NotionBlockElement
    ) -> bool:
        """Check if a block can have children."""
        element_name = element.__name__
        if element_name in self._child_prefixes:
            return True

        if hasattr(block, "toggle") and hasattr(block.toggle, "children"):
            return True
        if hasattr(block, "column_list") and hasattr(block.column_list, "children"):
            return True
        if hasattr(block, "column") and hasattr(block.column, "children"):
            return True
        if hasattr(block, "code") and hasattr(block.code, "rich_text"):
            return True  # Code blocks can have content
        if hasattr(block, "table") and hasattr(block.table, "children"):
            return True  # Tables can have rows
        if hasattr(block, "heading_1") and hasattr(block.heading_1, "children"):
            return True
        if hasattr(block, "heading_2") and hasattr(block.heading_2, "children"):
            return True
        if hasattr(block, "heading_3") and hasattr(block.heading_3, "children"):
            return True

        return False

    def _get_child_prefix(self, element: NotionBlockElement) -> str:
        """Determine the child prefix for the element type."""
        element_name = element.__name__
        return self._child_prefixes.get(element_name, "|")

    def _convert_children_text(self, text: str) -> list[BlockCreateRequest]:
        """Recursively convert children text."""
        if not text.strip():
            return []
        child_processor = MarkdownToNotionConverter(self._block_registry)
        child_results = child_processor._process_lines(text)
        return child_results.extract_blocks()

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

    @staticmethod
    def _normalize_to_list(result: BlockCreateResult) -> list[BlockCreateRequest]:
        """Normalize the result to a list."""
        if result is None:
            return []
        return result if isinstance(result, list) else [result]
