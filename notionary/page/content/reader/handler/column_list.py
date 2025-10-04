from typing import override

from notionary.blocks.enums import BlockType
from notionary.blocks.schemas import Block
from notionary.page.content.reader.context import BlockRenderingContext
from notionary.page.content.reader.handler.base import BlockRenderer


class ColumnListRenderer(BlockRenderer):
    START_MARKER = "::: columns"
    END_MARKER = ":::"

    @override
    def _can_handle(self, block: Block) -> bool:
        return block.type == BlockType.COLUMN_LIST

    @override
    async def _process(self, context: BlockRenderingContext) -> None:
        column_list_start = self.START_MARKER

        if context.indent_level > 0:
            column_list_start = context.indent_text(column_list_start)

        children_markdown = await context.render_children()

        column_list_end = self.END_MARKER
        if context.indent_level > 0:
            column_list_end = context.indent_text(column_list_end)

        if children_markdown:
            context.markdown_result = f"{column_list_start}\n{children_markdown}\n{column_list_end}"
        else:
            context.markdown_result = f"{column_list_start}\n{column_list_end}"
