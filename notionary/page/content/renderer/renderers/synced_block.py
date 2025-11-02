from typing import override

from notionary.blocks.schemas import Block, BlockType
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.base import BlockRenderer


class SyncedBlockRenderer(BlockRenderer):
    @override
    def _can_handle(self, block: Block) -> bool:
        return block.type == BlockType.SYNCED_BLOCK

    @override
    async def _process(self, context: MarkdownRenderingContext) -> None:
        if not context.block.synced_block:
            context.markdown_result = ""
            return

        synced_data = context.block.synced_block

        is_original = synced_data.synced_from is None

        if is_original:
            await self._render_original_block(context)
        else:
            await self._render_duplicate_block(
                context, synced_data.synced_from.block_id
            )

    async def _render_original_block(self, context: MarkdownRenderingContext) -> None:
        syntax = self._syntax_registry.get_synced_block_syntax()

        # Add marker for original synced block
        marker = f"{syntax.start_delimiter} Original Synced Block"

        if context.indent_level > 0:
            marker = context.indent_text(marker)

        # Render children
        children_markdown = await context.render_children()

        if children_markdown:
            context.markdown_result = (
                f"{marker}\n\n{children_markdown}\n\n{syntax.end_delimiter}"
            )
        else:
            context.markdown_result = f"{marker}\n\n{syntax.end_delimiter}"

    async def _render_duplicate_block(
        self, context: MarkdownRenderingContext, original_block_id: str
    ) -> None:
        syntax = self._syntax_registry.get_synced_block_syntax()

        reference = f"{syntax.start_delimiter} Synced from: {original_block_id} {syntax.end_delimiter}"

        if context.indent_level > 0:
            reference = context.indent_text(reference)

        context.markdown_result = reference
