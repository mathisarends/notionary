from typing import override

from notionary.blocks.mappings.callout import CalloutMapper
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
        return CalloutMapper.match_notion(context.block)

    @override
    async def _process(self, context: BlockRenderingContext) -> None:
        icon, content = await self._extract_callout_info(context.block)

        if not content:
            context.markdown_result = ""
            context.was_processed = True
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

        context.was_processed = True

    async def _extract_callout_info(self, block: Block) -> tuple[str, str]:
        if not block.callout:
            return "", ""

        icon = ""
        if block.callout.icon and hasattr(block.callout.icon, "emoji"):
            icon = block.callout.icon.emoji or ""

        content = ""
        if block.callout.rich_text:
            content = await self._rich_text_markdown_converter.to_markdown(block.callout.rich_text)

        return icon, content
