import re
from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter
from notionary.blocks.table.table_element import TableElement
from notionary.blocks.table.table_models import CreateTableRowBlock, TableRowBlock
from notionary.page.writer.handler import LineHandler, LineProcessingContext


class TableHandler(LineHandler):
    """Handles table specific logic with batching."""

    def __init__(self):
        super().__init__()
        self._table_row_pattern = re.compile(r"^\s*\|(.+)\|\s*$")
        self._separator_pattern = re.compile(r"^\s*\|([\s\-:|]+)\|\s*$")

    def _can_handle(self, context: LineProcessingContext) -> bool:
        if self._is_inside_parent_context(context):
            return False
        return self._is_table_start(context)

    def _process(self, context: LineProcessingContext) -> None:
        if not self._is_table_start(context):
            return

        self._process_complete_table(context)
        context.was_processed = True
        context.should_continue = True

    def _is_inside_parent_context(self, context: LineProcessingContext) -> bool:
        """Check if we're currently inside any parent context (toggle, heading, etc.)."""
        return len(context.parent_stack) > 0

    def _is_table_start(self, context: LineProcessingContext) -> bool:
        """Check if this line starts a table."""
        return self._table_row_pattern.match(context.line.strip()) is not None

    def _process_complete_table(self, context: LineProcessingContext) -> None:
        """Process the entire table in one go."""
        # Create table element
        table_element = TableElement()
        result = table_element.markdown_to_notion(context.line)
        if not result:
            return

        block = result if not isinstance(result, list) else result[0]

        # Collect all table lines (including the current one)
        table_lines = [context.line]
        remaining_lines = context.get_remaining_lines()
        lines_to_consume = 0

        # Find all consecutive table rows
        for i, line in enumerate(remaining_lines):
            line_stripped = line.strip()
            if not line_stripped:
                # Empty line - continue to allow for spacing in tables
                table_lines.append(line)
                continue

            if self._table_row_pattern.match(
                line_stripped
            ) or self._separator_pattern.match(line_stripped):
                table_lines.append(line)
            else:
                # Not a table line - stop here
                lines_to_consume = i
                break
        else:
            # Consumed all remaining lines
            lines_to_consume = len(remaining_lines)

        # Process the table content
        table_rows, separator_found = self._process_table_lines(table_lines)

        table = block.table
        table.children = table_rows
        table.has_column_header = bool(separator_found)

        # Tell the main loop to skip the consumed lines
        context.lines_consumed = lines_to_consume
        context.result_blocks.append(block)

    def _process_table_lines(
        self, table_lines: list[str]
    ) -> tuple[list[CreateTableRowBlock], bool]:
        """Process all table lines and return rows and separator status."""
        table_rows = []
        separator_found = False

        for line in table_lines:
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
        return self._separator_pattern.match(line) is not None

    def _create_table_row_from_line(self, line: str) -> CreateTableRowBlock:
        cells = self._parse_table_row(line)
        rich_text_cells = [self._convert_cell_to_rich_text(cell) for cell in cells]
        table_row = TableRowBlock(cells=rich_text_cells)
        return CreateTableRowBlock(table_row=table_row)

    def _convert_cell_to_rich_text(self, cell: str) -> list[RichTextObject]:
        rich_text = TextInlineFormatter.parse_inline_formatting(cell)
        if not rich_text:
            rich_text = [RichTextObject.from_plain_text(cell)]
        return rich_text

    def _parse_table_row(self, row_text: str) -> list[str]:
        row_content = row_text.strip()

        if row_content.startswith("|"):
            row_content = row_content[1:]
        if row_content.endswith("|"):
            row_content = row_content[:-1]

        return [cell.strip() for cell in row_content.split("|")]
