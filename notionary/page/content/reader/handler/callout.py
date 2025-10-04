from typing import override

from notionary.blocks.enums import BlockType
from notionary.blocks.mappings.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.blocks.schemas import Block
from notionary.page.content.reader.context import BlockRenderingContext
from notionary.page.content.reader.handler.base import BlockRenderer


class CalloutRenderer(BlockRenderer):
    CALLOUT_START = ":::"
    CALLOUT_END = ":::"

    def __init__(self, rich_text_markdown_converter: RichTextToMarkdownConverter | None = None) -> None:
        super().__init__()
        self._rich_text_markdown_converter = rich_text_markdown_converter or RichTextToMarkdownConverter()

    @override
    def _can_handle(self, context: BlockRenderingContext) -> bool:
        block = context.block
        return block.type == BlockType.CALLOUT

    @override
    async def _process(self, context: BlockRenderingContext) -> None:
        icon = await self._extract_callout_icon(context.block)
        content = await self._extract_callout_content(context.block)

        if not content:
            context.markdown_result = ""
            return

        # Build callout structure
        callout_header = f"{self.CALLOUT_START} callout"
        if icon:
            callout_header = f"{self.CALLOUT_START} callout {icon}"

        if context.indent_level > 0:
            callout_header = context.indent_text(callout_header)

        # Process children if they exist
        children_markdown = await context.render_children()

        callout_end = self.CALLOUT_END
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
