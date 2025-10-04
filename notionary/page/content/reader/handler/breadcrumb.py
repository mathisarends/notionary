from typing import override

from notionary.blocks.schemas import BlockType
from notionary.page.content.reader.context import BlockRenderingContext
from notionary.page.content.reader.handler.base import BlockRenderer


class BreadcrumbRenderer(BlockRenderer):
    BREADCRUMB_MARKDOWN = "[breadcrumb]"

    @override
    def _can_handle(self, context: BlockRenderingContext) -> bool:
        return context.block.type == BlockType.BREADCRUMB

    @override
    async def _process(self, context: BlockRenderingContext) -> None:
        breadcrumb_markdown = self.BREADCRUMB_MARKDOWN

        if context.indent_level > 0:
            breadcrumb_markdown = context.indent_text(breadcrumb_markdown)

        context.markdown_result = breadcrumb_markdown
