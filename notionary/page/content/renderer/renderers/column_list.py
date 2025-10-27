from typing import override

from notionary.blocks.enums import BlockType
from notionary.blocks.schemas import Block
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.base import BlockRenderer


class ColumnListRenderer(BlockRenderer):
    @override
    def _can_handle(self, block: Block) -> bool:
        return block.type == BlockType.COLUMN_LIST

    @override
    async def _process(self, context: MarkdownRenderingContext) -> None:
        column_list_start = self._format_column_list_start(context.indent_level)
        children_markdown = await self._render_children_with_indentation(context)

        if children_markdown:
            context.markdown_result = f"{column_list_start}\n{children_markdown}"
        else:
            context.markdown_result = column_list_start

    def _format_column_list_start(self, indent_level: int) -> str:
        delimiter = self._get_column_list_delimiter()

        if indent_level > 0:
            indent = "    " * indent_level
            return f"{indent}{delimiter}"

        return delimiter

    def _get_column_list_delimiter(self) -> str:
        return self._syntax_registry.get_column_list_syntax().start_delimiter

    async def _render_children_with_indentation(
        self, context: MarkdownRenderingContext
    ) -> str:
        original_indent = context.indent_level
        context.indent_level += 1

        children_markdown = await context.render_children()

        context.indent_level = original_indent

        return children_markdown
