from typing import override

from notionary.blocks.enums import BlockType
from notionary.blocks.schemas import Block
from notionary.page.content.reader.context import BlockRenderingContext
from notionary.page.content.reader.handler.base import BlockRenderer


class DividerRenderer(BlockRenderer):
    DIVIDER_MARKDOWN = "---"

    @override
    def _can_handle(self, block: Block) -> bool:
        return block.type == BlockType.DIVIDER

    @override
    async def _process(self, context: BlockRenderingContext) -> None:
        divider_markdown = self.DIVIDER_MARKDOWN

        if context.indent_level > 0:
            divider_markdown = context.indent_text(divider_markdown)

        context.markdown_result = divider_markdown
