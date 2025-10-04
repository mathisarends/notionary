from typing import override

from notionary.blocks.mappings.divider import DividerMapper
from notionary.page.content.reader.context import BlockRenderingContext
from notionary.page.content.reader.handler.base import BlockRenderer


class DividerRenderer(BlockRenderer):
    DIVIDER_MARKDOWN = "---"

    @override
    def _can_handle(self, context: BlockRenderingContext) -> bool:
        return DividerMapper.match_notion(context.block)

    @override
    async def _process(self, context: BlockRenderingContext) -> None:
        divider_markdown = self.DIVIDER_MARKDOWN

        if context.indent_level > 0:
            divider_markdown = context.indent_text(divider_markdown)

        context.markdown_result = divider_markdown
        context.was_processed = True
