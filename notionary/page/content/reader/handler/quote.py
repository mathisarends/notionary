from typing import override

from notionary.blocks.mappings.quote import QuoteMapper
from notionary.blocks.mappings.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.blocks.schemas import Block
from notionary.page.content.reader.context import BlockRenderingContext
from notionary.page.content.reader.handler.base import BlockRenderer


class QuoteRenderer(BlockRenderer):
    QUOTE_PREFIX = "> "

    def __init__(self, rich_text_markdown_converter: RichTextToMarkdownConverter | None = None) -> None:
        super().__init__()
        self._rich_text_markdown_converter = rich_text_markdown_converter or RichTextToMarkdownConverter()

    @override
    def _can_handle(self, context: BlockRenderingContext) -> bool:
        return QuoteMapper.match_notion(context.block)

    @override
    async def _process(self, context: BlockRenderingContext) -> None:
        markdown = await self._convert_quote_to_markdown(context.block)

        if not markdown:
            context.markdown_result = ""
            context.was_processed = True
            return

        quote_lines = markdown.split("\n")
        quote_markdown = "\n".join(f"{self.QUOTE_PREFIX}{line}" for line in quote_lines)

        if context.indent_level > 0:
            quote_markdown = context.indent_text(quote_markdown)

        children_markdown = await context.render_children_with_additional_indent(1)

        if children_markdown:
            context.markdown_result = f"{quote_markdown}\n{children_markdown}"
        else:
            context.markdown_result = quote_markdown

        context.was_processed = True

    async def _convert_quote_to_markdown(self, block: Block) -> str | None:
        if not block.quote or not block.quote.rich_text:
            return None

        return await self._rich_text_markdown_converter.to_markdown(block.quote.rich_text)
