import re

from notionary.blocks.mappings.rich_text.markdown_rich_text_converter import MarkdownRichTextConverter
from notionary.blocks.mappings.rich_text.models import RichText
from notionary.blocks.schemas import CreateTableBlock, CreateTableRowBlock, TableData, TableRowData
from notionary.page.content.parser.parsers import BlockParsingContext, LineParser


class TableParser(LineParser):
    TABLE_ROW_PATTERN = r"^\s*\|(.+)\|\s*$"
    SEPARATOR_PATTERN = r"^\s*\|([\s\-:|]+)\|\s*$"

    def __init__(self, markdown_rich_text_converter: MarkdownRichTextConverter | None = None) -> None:
        super().__init__()
        self.markdown_rich_text_converter = markdown_rich_text_converter or MarkdownRichTextConverter()
        self._table_row_pattern = re.compile(self.TABLE_ROW_PATTERN)
        self._separator_pattern = re.compile(self.SEPARATOR_PATTERN)

    def _can_handle(self, context: BlockParsingContext) -> bool:
        if context.is_inside_parent_context():
            return False
        return self._is_table_start(context)

    async def _process(self, context: BlockParsingContext) -> None:
        if not self._is_table_start(context):
            return

        await self._process_complete_table(context)

    def _is_table_start(self, context: BlockParsingContext) -> bool:
        return self._table_row_pattern.match(context.line.strip()) is not None

    async def _process_complete_table(self, context: BlockParsingContext) -> None:
        table_lines = [context.line]
        remaining_lines = context.get_remaining_lines()
        lines_consumed = self._collect_table_lines(table_lines, remaining_lines)

        block = await self._create_table_block(table_lines)

        if block:
            context.lines_consumed = lines_consumed
            context.result_blocks.append(block)

    def _collect_table_lines(self, table_lines: list[str], remaining_lines: list[str]) -> int:
        lines_consumed = 0

        for index, line in enumerate(remaining_lines):
            line_stripped = line.strip()

            if not line_stripped:
                table_lines.append(line)
                continue

            if self._is_table_line(line_stripped):
                table_lines.append(line)
            else:
                lines_consumed = index
                break
        else:
            lines_consumed = len(remaining_lines)

        return lines_consumed

    def _is_table_line(self, line: str) -> bool:
        return self._table_row_pattern.match(line) or self._separator_pattern.match(line)

    async def _create_table_block(self, table_lines: list[str]) -> CreateTableBlock | None:
        if not table_lines:
            return None

        first_row = self._find_first_table_row(table_lines)
        if not first_row:
            return None

        header_cells = self._parse_table_row(first_row)
        column_count = len(header_cells)

        table_rows, has_separator = await self._process_table_rows(table_lines)

        table_data = TableData(
            table_width=column_count,
            has_column_header=has_separator,
            has_row_header=False,
            children=table_rows,
        )

        return CreateTableBlock(table=table_data)

    def _find_first_table_row(self, table_lines: list[str]) -> str | None:
        for line in table_lines:
            line_stripped = line.strip()
            if line_stripped and self._table_row_pattern.match(line_stripped):
                return line_stripped
        return None

    async def _process_table_rows(self, table_lines: list[str]) -> tuple[list[CreateTableRowBlock], bool]:
        table_rows = []
        has_separator = False

        for line in table_lines:
            line_stripped = line.strip()

            if not line_stripped:
                continue

            if self._is_separator_line(line_stripped):
                has_separator = True
                continue

            if self._table_row_pattern.match(line_stripped):
                table_row = await self._create_table_row(line_stripped)
                table_rows.append(table_row)

        return table_rows, has_separator

    def _is_separator_line(self, line: str) -> bool:
        return self._separator_pattern.match(line) is not None

    async def _create_table_row(self, line: str) -> CreateTableRowBlock:
        cells = self._parse_table_row(line)
        rich_text_cells = await self._convert_cells_to_rich_text(cells)
        table_row_data = TableRowData(cells=rich_text_cells)
        return CreateTableRowBlock(table_row=table_row_data)

    async def _convert_cells_to_rich_text(self, cells: list[str]) -> list[list[RichText]]:
        rich_text_cells = []

        for cell in cells:
            rich_text = await self.markdown_rich_text_converter.to_rich_text(cell)
            rich_text_cells.append(rich_text)

        return rich_text_cells

    def _parse_table_row(self, row_text: str) -> list[str]:
        row_content = row_text.strip()

        if row_content.startswith("|"):
            row_content = row_content[1:]
        if row_content.endswith("|"):
            row_content = row_content[:-1]

        return row_content.split("|")
