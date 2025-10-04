from typing import override

from notionary.blocks.schemas import Block
from notionary.page.content.reader.context import BlockRenderingContext
from notionary.page.content.reader.handler.base import BlockRenderer
from notionary.utils.mixins.logging import LoggingMixin


class FallbackRenderer(BlockRenderer, LoggingMixin):
    @override
    def _can_handle(self, block: Block) -> bool:
        return True

    @override
    async def _process(self, context: BlockRenderingContext) -> None:
        block_type = context.block.type.value if context.block.type else "unknown"
        self.logger.warning(f"No handler found for block type: {block_type}")

        fallback_message = f"[Unsupported block type: {block_type}]"

        if context.indent_level > 0:
            fallback_message = context.indent_text(fallback_message)

        context.markdown_result = fallback_message
