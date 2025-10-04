from typing import override

from notionary.blocks.enums import BlockType
from notionary.blocks.schemas import Block
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.base import BlockRenderer


class DividerRenderer(BlockRenderer):
    DIVIDER_MARKDOWN = "---"

    @override
    def _can_handle(self, block: Block) -> bool:
        return block.type == BlockType.DIVIDER

    @override
    async def _process(self, context: MarkdownRenderingContext) -> None:
        divider_markdown = self.DIVIDER_MARKDOWN

        if context.indent_level > 0:
            divider_markdown = context.indent_text(divider_markdown)

        context.markdown_result = divider_markdown
