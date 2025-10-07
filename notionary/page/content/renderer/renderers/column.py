from typing import override

from notionary.blocks.enums import BlockType
from notionary.blocks.schemas import Block
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.base import BlockRenderer


class ColumnRenderer(BlockRenderer):
    @override
    def _can_handle(self, block: Block) -> bool:
        return block.type == BlockType.COLUMN

    @override
    async def _process(self, context: MarkdownRenderingContext) -> None:
        column_start = self._extract_column_start(context.block)

        if context.indent_level > 0:
            column_start = context.indent_text(column_start)

        children_markdown = await context.render_children()

        syntax = self._syntax_registry.get_column_syntax()
        column_end = syntax.end_delimiter
        if context.indent_level > 0:
            column_end = context.indent_text(column_end, spaces=context.indent_level * 4)

        if children_markdown:
            context.markdown_result = f"{column_start}\n{children_markdown}\n{column_end}"
        else:
            context.markdown_result = f"{column_start}\n{column_end}"

    def _extract_column_start(self, block: Block) -> str:
        syntax = self._syntax_registry.get_column_syntax()
        base_start = syntax.start_delimiter

        if not block.column:
            return base_start

        width_ratio = block.column.width_ratio
        if width_ratio:
            return f"{base_start} {width_ratio}"
        else:
            return base_start
