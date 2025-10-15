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
        content = await self._extract_callout_content(context.block)

        if not content:
            context.markdown_result = ""
            return

        icon = await self._extract_callout_icon(context.block)

        callout_start_delimiter = self._syntax_registry.get_callout_syntax().start_delimiter

        result = f'{callout_start_delimiter}({content} "{icon}")' if icon else f"{callout_start_delimiter}({content})"

        if context.indent_level > 0:
            result = context.indent_text(result)

        context.markdown_result = result

    async def _extract_callout_icon(self, block: Block) -> str:
        if not block.callout or not block.callout.icon:
            return ""
        return block.callout.icon.emoji or ""

    async def _extract_callout_content(self, block: Block) -> str:
        if not block.callout or not block.callout.rich_text:
            return ""
        return await self._rich_text_markdown_converter.to_markdown(block.callout.rich_text)
