import re
from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter
from notionary.blocks.table.table_element import TableElement
from notionary.blocks.table.table_models import CreateTableRowBlock, TableRowBlock
from notionary.page.formatting.line_handler import LineHandler, LineProcessingContext


class TableHandler(LineHandler):
    """Handles table specific logic."""

    def __init__(self):
        super().__init__()
        self._table_row_pattern = re.compile(r"^\s*\|(.+)\|\s*$")
        self._separator_pattern = re.compile(r"^\s*\|([\s\-:|]+)\|\s*$")

    def _can_handle(self, context: LineProcessingContext) -> bool:
        return self._is_table_end(context) or self._is_table_row(context)

    def _process(self, context: LineProcessingContext) -> None:
        if self._is_table_end(context):
            self._finalize_table(context)
            # Don't set was_processed=True, let the line be processed as a regular line
            return

        if self._is_table_row(context):
            self._add_table_row(context)
            context.was_processed = True
            context.should_continue = True

    def _is_table_end(self, context: LineProcessingContext) -> bool:
        """Check if we need to end a table."""
        if not context.parent_stack:
            return False

        current_parent = context.parent_stack[-1]
        if current_parent.element_type.__name__ != "TableElement":
            return False

        # If line doesn't match table pattern and is not empty, end table
        return (
            not self._table_row_pattern.match(context.line.strip())
            and context.line.strip()
        )

    def _is_table_row(self, context: LineProcessingContext) -> bool:
        """Check if this is a table row in an active table."""
        if not context.parent_stack:
            return False

        current_parent = context.parent_stack[-1]
        return (
            isinstance(current_parent.element_type, type)
            and issubclass(current_parent.element_type, TableElement)
            and current_parent.child_prefix == "TABLE_ROW"
            and self._table_row_pattern.match(context.line.strip())
        )

    def _finalize_table(self, context: LineProcessingContext) -> None:
        """Finalize a table and convert child lines to table rows."""
        table_context = context.parent_stack.pop()

        if not table_context.has_children():
            context.result_blocks.add(
                table_context.start_position, context.current_pos, table_context.block
            )
            return

        table_rows, separator_found = self._process_table_lines(
            table_context.child_lines
        )

        table_context.block.table.children = table_rows
        if table_rows and separator_found:
            table_context.block.table.has_column_header = True

        context.result_blocks.add(
            table_context.start_position, context.current_pos, table_context.block
        )

    def _process_table_lines(
        self, child_lines: list[str]
    ) -> tuple[list[CreateTableRowBlock], bool]:
        """Process all table lines and return table rows and separator status."""
        table_rows = []
        separator_found = False

        for line in child_lines:
            line = line.strip()
            if not line:
                continue

            if self._is_separator_line(line):
                separator_found = True
                continue

            if self._table_row_pattern.match(line):
                table_row = self._create_table_row_from_line(line)
                table_rows.append(table_row)

        return table_rows, separator_found

    def _is_separator_line(self, line: str) -> bool:
        """Check if line is a table separator (| ---- | ---- |)."""
        return self._separator_pattern.match(line) is not None

    def _create_table_row_from_line(self, line: str) -> CreateTableRowBlock:
        """Create a table row block from a line."""
        cells = self._parse_table_row(line)
        rich_text_cells = [self._convert_cell_to_rich_text(cell) for cell in cells]

        table_row = TableRowBlock(cells=rich_text_cells)
        return CreateTableRowBlock(table_row=table_row)

    def _convert_cell_to_rich_text(self, cell: str) -> list[RichTextObject]:
        """Convert a single cell to rich text objects."""
        rich_text = TextInlineFormatter.parse_inline_formatting(cell)
        if not rich_text:
            rich_text = [RichTextObject.from_plain_text(cell)]
        return rich_text

    def _add_table_row(self, context: LineProcessingContext) -> None:
        """Add a table row to the current table."""
        context.parent_stack[-1].add_child_line(context.line)

    def _parse_table_row(self, row_text: str) -> list[str]:
        """Convert table row text to cell contents."""
        row_content = row_text.strip()

        if row_content.startswith("|"):
            row_content = row_content[1:]
        if row_content.endswith("|"):
            row_content = row_content[:-1]

        return [cell.strip() for cell in row_content.split("|")]
