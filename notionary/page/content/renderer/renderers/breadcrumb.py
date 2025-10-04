from typing import override

from notionary.blocks.schemas import Block, BlockType
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.base import BlockRenderer


class BreadcrumbRenderer(BlockRenderer):
    BREADCRUMB_MARKDOWN = "[breadcrumb]"

    @override
    def _can_handle(self, block: Block) -> bool:
        return block.type == BlockType.BREADCRUMB

    @override
    async def _process(self, context: MarkdownRenderingContext) -> None:
        breadcrumb_markdown = self.BREADCRUMB_MARKDOWN

        if context.indent_level > 0:
            breadcrumb_markdown = context.indent_text(breadcrumb_markdown)

        context.markdown_result = breadcrumb_markdown
