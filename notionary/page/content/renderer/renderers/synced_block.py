from typing import override

from notionary.blocks.schemas import Block, BlockType
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.base import BlockRenderer


class SyncedBlockRenderer(BlockRenderer):
    EMPTY_CONTENT_PLACEHOLDER = "no content available"

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
            await self._render_duplicate_block(context)

    async def _render_original_block(self, context: MarkdownRenderingContext) -> None:
        syntax = self._syntax_registry.get_synced_block_syntax()
        marker = f"{syntax.start_delimiter} Synced Block"

        if context.indent_level > 0:
            marker = context.indent_text(marker)

        original_indent = context.indent_level
        context.indent_level += 1
        children_markdown = await context.render_children()
        context.indent_level = original_indent

        if children_markdown:
            context.markdown_result = f"{marker}\n{children_markdown}"
        else:
            context.indent_level += 1
            no_content = context.indent_text(self.EMPTY_CONTENT_PLACEHOLDER)
            context.indent_level = original_indent
            context.markdown_result = f"{marker}\n{no_content}"

    async def _render_duplicate_block(self, context: MarkdownRenderingContext) -> None:
        synced_data = context.block.synced_block
        syntax = self._syntax_registry.get_synced_block_syntax()
        reference = (
            f"{syntax.start_delimiter} Synced from: {synced_data.synced_from.block_id}"
        )

        if context.indent_level > 0:
            reference = context.indent_text(reference)

        original_indent = context.indent_level
        context.indent_level += 1
        children_markdown = await context.render_children()
        context.indent_level = original_indent

        if children_markdown:
            context.markdown_result = f"{reference}\n{children_markdown}"
        else:
            context.markdown_result = reference
