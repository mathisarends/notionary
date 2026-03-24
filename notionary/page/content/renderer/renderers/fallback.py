import logging
from typing import override

from notionary.blocks.schemas import Block
from notionary.markdown.syntax.definition.registry import SyntaxDefinitionRegistry
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.base import BlockRenderer

logger = logging.getLogger(__name__)


class FallbackRenderer(BlockRenderer):
    def __init__(self, syntax_registry: SyntaxDefinitionRegistry) -> None:
        super().__init__(syntax_registry=syntax_registry)

    @override
    def _can_handle(self, block: Block) -> bool:
        return True

    @override
    async def _process(self, context: MarkdownRenderingContext) -> None:
        block_type = context.block.type.value if context.block.type else "unknown"
        logger.warning(f"No handler found for block type: {block_type}")

        fallback_message = f"[Unsupported block type: {block_type}]"

        if context.indent_level > 0:
            fallback_message = context.indent_text(fallback_message)

        context.markdown_result = fallback_message
