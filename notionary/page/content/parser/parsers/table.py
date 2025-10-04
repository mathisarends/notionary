import re

from notionary.blocks.mappings.table import TableMapper
from notionary.page.content.parser.parsers import LineParser, LineProcessingContext


class TableParser(LineParser):
    """Handles table specific logic with batching."""

    def __init__(self) -> None:
        super().__init__()
        self._table_row_pattern = re.compile(r"^\s*\|(.+)\|\s*$")
        self._separator_pattern = re.compile(r"^\s*\|([\s\-:|]+)\|\s*$")

    def _can_handle(self, context: LineProcessingContext) -> bool:
        if self._is_inside_parent_context(context):
            return False
        return self._is_table_start(context)

    async def _process(self, context: LineProcessingContext) -> None:
        if not self._is_table_start(context):
            return

        await self._process_complete_table(context)
        context.was_processed = True
        context.should_continue = True

    def _is_inside_parent_context(self, context: LineProcessingContext) -> bool:
        """Check if we're currently inside any parent context (toggle, heading, etc.)."""
        return len(context.parent_stack) > 0

    def _is_table_start(self, context: LineProcessingContext) -> bool:
        """Check if this line starts a table."""
        return self._table_row_pattern.match(context.line.strip()) is not None

    async def _process_complete_table(self, context: LineProcessingContext) -> None:
        """Process the entire table in one go using TableMapper."""
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

            if self._table_row_pattern.match(line_stripped) or self._separator_pattern.match(line_stripped):
                table_lines.append(line)
            else:
                # Not a table line - stop here
                lines_to_consume = i
                break
        else:
            lines_to_consume = len(remaining_lines)

        block = await TableMapper.create_from_markdown_table(table_lines)

        if block:
            context.lines_consumed = lines_to_consume
            context.result_blocks.append(block)
