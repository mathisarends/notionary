from typing import override

from notionary.blocks.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.blocks.schemas import Block, BlockType
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.base import BlockRenderer
from notionary.page.content.syntax.service import SyntaxRegistry


class CalloutRenderer(BlockRenderer):
    def __init__(
        self,
        syntax_registry: SyntaxRegistry | None = None,
        rich_text_markdown_converter: RichTextToMarkdownConverter | None = None,
    ) -> None:
        super().__init__(syntax_registry=syntax_registry)
        self._rich_text_markdown_converter = rich_text_markdown_converter or RichTextToMarkdownConverter()

    @override
    def _can_handle(self, block: Block) -> bool:
        return block.type == BlockType.CALLOUT

    @override
    async def _process(self, context: MarkdownRenderingContext) -> None:
        icon = await self._extract_callout_icon(context.block)
        content = await self._extract_callout_content(context.block)

        if not content:
            context.markdown_result = ""
            return

        syntax = self._syntax_registry.get_callout_syntax()

        # Build callout structure
        # Extract just the base part before the regex pattern
        callout_type = syntax.start_delimiter.split()[1]  # Gets "callout" from "::: callout"
        callout_header = f"{self._syntax_registry.MULTI_LINE_BLOCK_DELIMITER} {callout_type}"
        if icon:
            callout_header = f"{self._syntax_registry.MULTI_LINE_BLOCK_DELIMITER} {callout_type} {icon}"

        if context.indent_level > 0:
            callout_header = context.indent_text(callout_header)

        # Process children if they exist
        children_markdown = await context.render_children()

        callout_end = syntax.end_delimiter
        if context.indent_level > 0:
            callout_end = context.indent_text(callout_end)

        # Combine content
        if children_markdown:
            context.markdown_result = f"{callout_header}\n{content}\n{children_markdown}\n{callout_end}"
        else:
            context.markdown_result = f"{callout_header}\n{content}\n{callout_end}"

    async def _extract_callout_icon(self, block: Block) -> str:
        if not block.callout or not block.callout.icon:
            return ""
        return block.callout.icon.emoji or ""

    async def _extract_callout_content(self, block: Block) -> str:
        if not block.callout or not block.callout.rich_text:
            return ""
        return await self._rich_text_markdown_converter.to_markdown(block.callout.rich_text)
