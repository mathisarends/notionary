from typing import override

from notionary.blocks.enums import BlockType
from notionary.blocks.schemas import Block
from notionary.page.content.reader.context import BlockRenderingContext
from notionary.page.content.reader.handler.base import BlockRenderer


class ColumnRenderer(BlockRenderer):
    BASE_START_MARKER = "::: column"
    END_MARKER = ":::"

    @override
    def _can_handle(self, context: BlockRenderingContext) -> bool:
        block = context.block
        return block.type == BlockType.COLUMN

    @override
    async def _process(self, context: BlockRenderingContext) -> None:
        column_start = self._extract_column_start(context.block)

        if context.indent_level > 0:
            column_start = context.indent_text(column_start)

        children_markdown = await context.render_children()

        column_end = self.END_MARKER
        if context.indent_level > 0:
            column_end = context.indent_text(column_end, spaces=context.indent_level * 4)

        if children_markdown:
            context.markdown_result = f"{column_start}\n{children_markdown}\n{column_end}"
        else:
            context.markdown_result = f"{column_start}\n{column_end}"

    def _extract_column_start(self, block: Block) -> str:
        if not block.column:
            return self.BASE_START_MARKER

        width_ratio = block.column.width_ratio
        if width_ratio:
            return f"{self.BASE_START_MARKER} {width_ratio}"
        else:
            return self.BASE_START_MARKER
