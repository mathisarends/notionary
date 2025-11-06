from typing import override

from notionary.blocks.schemas import Block, BlockType
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.base import BlockRenderer
from notionary.page.content.syntax.definition import SyntaxDefinitionRegistry
from notionary.rich_text.rich_text_to_markdown.converter import (
    RichTextToMarkdownConverter,
)


class TableRenderer(BlockRenderer):
    MINIMUM_COLUMN_WIDTH = 3

    def __init__(
        self,
        syntax_registry: SyntaxDefinitionRegistry,
        rich_text_markdown_converter: RichTextToMarkdownConverter,
    ) -> None:
        super().__init__(syntax_registry=syntax_registry)
        self._rich_text_markdown_converter = rich_text_markdown_converter
        self._table_syntax = self._syntax_registry.get_table_syntax()

    @override
    def _can_handle(self, block: Block) -> bool:
        return block.type == BlockType.TABLE

    @override
    async def _process(self, context: MarkdownRenderingContext) -> None:
        table_markdown = await self._build_table_markdown(context.block)

        if not table_markdown:
            context.markdown_result = ""
            return

        if context.indent_level > 0:
            table_markdown = context.indent_text(table_markdown)

        children_markdown = await context.render_children_with_additional_indent(1)

        if children_markdown:
            context.markdown_result = f"{table_markdown}\n{children_markdown}"
        else:
            context.markdown_result = table_markdown

    async def _build_table_markdown(self, block: Block) -> str:
        if not block.table or not block.has_children or not block.children:
            return ""

        rows = []
        for row_block in block.children:
            if row_block.type != BlockType.TABLE_ROW or not row_block.table_row:
                continue

            row_cells = await self._extract_row_cells(row_block)
            rows.append(row_cells)

        if not rows:
            return ""

        max_columns = max(len(row) for row in rows)
        normalized_rows = self._normalize_row_lengths(rows, max_columns)
        column_widths = self._calculate_column_widths(normalized_rows, max_columns)

        markdown_lines = []

        first_row = normalized_rows[0]
        formatted_first_row = self._format_row(first_row, column_widths)
        markdown_lines.append(formatted_first_row)

        separator_line = self._create_separator_line(column_widths)
        markdown_lines.append(separator_line)

        remaining_rows = normalized_rows[1:]
        for row in remaining_rows:
            formatted_row = self._format_row(row, column_widths)
            markdown_lines.append(formatted_row)

        return "\n".join(markdown_lines)

    def _normalize_row_lengths(
        self, rows: list[list[str]], target_length: int
    ) -> list[list[str]]:
        return [row + [""] * (target_length - len(row)) for row in rows]

    def _calculate_column_widths(
        self, rows: list[list[str]], num_columns: int
    ) -> list[int]:
        widths = [max(len(row[i]) for row in rows) for i in range(num_columns)]
        return [max(width, self.MINIMUM_COLUMN_WIDTH) for width in widths]

    def _format_row(self, cells: list[str], column_widths: list[int]) -> str:
        centered_cells = [cell.center(column_widths[i]) for i, cell in enumerate(cells)]
        delimiter = self._table_syntax.start_delimiter
        return f"{delimiter} {f' {delimiter} '.join(centered_cells)} {delimiter}"

    def _create_separator_line(self, column_widths: list[int]) -> str:
        separators = ["-" * width for width in column_widths]
        delimiter = self._table_syntax.start_delimiter
        return f"{delimiter} {f' {delimiter} '.join(separators)} {delimiter}"

    def _has_column_header(self, block: Block) -> bool:
        if not block.table:
            return False
        return block.table.has_column_header or False

    def _has_row_header(self, block: Block) -> bool:
        if not block.table:
            return False
        return block.table.has_row_header or False

    def _get_table_width(self, block: Block) -> int:
        if not block.table:
            return 0
        return block.table.table_width or 0

    async def _extract_row_cells(self, row_block: Block) -> list[str]:
        if not row_block.table_row or not row_block.table_row.cells:
            return []

        cells = []
        for cell in row_block.table_row.cells:
            cell_text = await self._rich_text_markdown_converter.to_markdown(cell)
            cells.append(cell_text or "")

        return cells
