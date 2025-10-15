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
        column_start = self._format_column_start(context.block, context.indent_level)
        children_markdown = await self._render_children_with_indentation(context)

        if children_markdown:
            context.markdown_result = f"{column_start}\n{children_markdown}"
        else:
            context.markdown_result = column_start

    def _format_column_start(self, block: Block, indent_level: int) -> str:
        column_start = self._build_column_start_tag(block)

        if indent_level > 0:
            indent = "    " * indent_level
            column_start = f"{indent}{column_start}"

        return column_start

    def _build_column_start_tag(self, block: Block) -> str:
        delimiter = self._syntax_registry.get_column_syntax().start_delimiter

        if not block.column:
            return delimiter

        width_ratio = block.column.width_ratio
        if width_ratio:
            return f"{delimiter} {width_ratio}"

        return delimiter

    async def _render_children_with_indentation(self, context: MarkdownRenderingContext) -> str:
        original_indent = context.indent_level
        context.indent_level += 1

        children_markdown = await context.render_children()

        context.indent_level = original_indent

        return children_markdown
