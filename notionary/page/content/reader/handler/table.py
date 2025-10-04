from typing import override

from notionary.blocks.mappings.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.blocks.schemas import Block, BlockType
from notionary.page.content.reader.context import BlockRenderingContext
from notionary.page.content.reader.handler.base import BlockRenderer


class TableRenderer(BlockRenderer):
    def __init__(self, rich_text_markdown_converter: RichTextToMarkdownConverter | None = None) -> None:
        super().__init__()
        self._rich_text_markdown_converter = rich_text_markdown_converter or RichTextToMarkdownConverter()

    @override
    def _can_handle(self, block: Block) -> bool:
        return block.type == BlockType.TABLE

    @override
    async def _process(self, context: BlockRenderingContext) -> None:
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

        has_column_header = self._has_column_header(block)

        rows = []
        for row_block in block.children:
            if row_block.type != BlockType.TABLE_ROW or not row_block.table_row:
                continue

            row_cells = await self._extract_row_cells(row_block)
            rows.append(row_cells)

        if not rows:
            return ""

        markdown_lines = []

        # Add header row if present
        if has_column_header and rows:
            header_row = rows[0]
            markdown_lines.append("| " + " | ".join(header_row) + " |")
            markdown_lines.append("| " + " | ".join(["---"] * len(header_row)) + " |")
            data_rows = rows[1:]
        else:
            data_rows = rows

        # Add data rows
        for row in data_rows:
            markdown_lines.append("| " + " | ".join(row) + " |")

        return "\n".join(markdown_lines)

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
