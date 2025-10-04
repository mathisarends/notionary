from typing import override

from notionary.blocks.schemas import BlockType
from notionary.page.content.reader.context import BlockRenderingContext
from notionary.page.content.reader.handler.base import BlockRenderer


class BreadcrumbRenderer(BlockRenderer):
    @override
    def _can_handle(self, context: BlockRenderingContext) -> bool:
        return context.block.type == BlockType.BREADCRUMB

    @override
    async def _process(self, context: BlockRenderingContext) -> None:
        # Breadcrumbs typically don't have meaningful markdown representation
        # We'll just output an empty string or a placeholder
        breadcrumb_markdown = ""

        if context.indent_level > 0:
            breadcrumb_markdown = context.indent_text(breadcrumb_markdown)

        children_markdown = await context.render_children_with_additional_indent(1)

        if children_markdown:
            context.markdown_result = (
                f"{breadcrumb_markdown}\n{children_markdown}" if breadcrumb_markdown else children_markdown
            )
        else:
            context.markdown_result = breadcrumb_markdown

        context.was_processed = True
