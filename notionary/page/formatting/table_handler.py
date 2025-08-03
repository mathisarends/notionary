import re
from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter
from notionary.blocks.table.table_models import CreateTableRowBlock, TableRowBlock
from notionary.page.formatting.line_handler import LineHandler, LineProcessingContext


class TableHandler(LineHandler):
    """Handles table specific logic."""

    def __init__(self):
        super().__init__()
        self._table_row_pattern = re.compile(r"^\s*\|(.+)\|\s*$")

    def _can_handle(self, context: LineProcessingContext) -> bool:
        return self._is_table_end(context) or self._is_table_row(context)

    def _process(self, context: LineProcessingContext) -> None:
        if self._is_table_end(context):
            self._finalize_table(context)
            # Don't set was_processed=True, let the line be processed as a regular line
        elif self._is_table_row(context):
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
            current_parent.element_type.__name__ == "TableElement"
            and current_parent.child_prefix == "TABLE_ROW"
            and self._table_row_pattern.match(context.line.strip())
        )

    def _finalize_table(self, context: LineProcessingContext) -> None:
        """Finalize a table and convert child lines to table rows."""
        table_context = context.parent_stack.pop()

        if table_context.has_children():
            table_rows = []
            separator_found = False

            for line in table_context.child_lines:
                line = line.strip()
                if not line:
                    continue

                # Check for separator line
                if re.match(r"^\s*\|([\s\-:|]+)\|\s*$", line):
                    separator_found = True
                    continue

                # Parse table row
                if self._table_row_pattern.match(line):
                    cells = self._parse_table_row(line)
                    rich_text_cells = []
                    for cell in cells:
                        rich_text = TextInlineFormatter.parse_inline_formatting(cell)
                        if not rich_text:
                            rich_text = [RichTextObject.from_plain_text(cell)]
                        rich_text_cells.append(rich_text)

                    table_row = TableRowBlock(cells=rich_text_cells)
                    table_rows.append(CreateTableRowBlock(table_row=table_row))

            table_context.block.table.children = table_rows

            if table_rows and separator_found:
                table_context.block.table.has_column_header = True

        context.result_blocks.add(
            table_context.start_position, context.current_pos, table_context.block
        )

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
