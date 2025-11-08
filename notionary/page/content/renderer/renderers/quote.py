from typing import override

from notionary.blocks.schemas import Block, BlockType
from notionary.markdown.syntax.definition.registry import SyntaxDefinitionRegistry
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.base import BlockRenderer
from notionary.rich_text.rich_text_to_markdown.converter import (
    RichTextToMarkdownConverter,
)


class QuoteRenderer(BlockRenderer):
    def __init__(
        self,
        syntax_registry: SyntaxDefinitionRegistry,
        rich_text_markdown_converter: RichTextToMarkdownConverter,
    ) -> None:
        super().__init__(syntax_registry=syntax_registry)
        self._rich_text_markdown_converter = rich_text_markdown_converter

    @override
    def _can_handle(self, block: Block) -> bool:
        return block.type == BlockType.QUOTE

    @override
    async def _process(self, context: MarkdownRenderingContext) -> None:
        markdown = await self._convert_quote_to_markdown(context.block)

        if not markdown:
            context.markdown_result = ""
            return

        syntax = self._syntax_registry.get_quote_syntax()
        quote_lines = markdown.split("\n")
        quote_markdown = "\n".join(
            f"{syntax.start_delimiter}{line}" for line in quote_lines
        )

        if context.indent_level > 0:
            quote_markdown = context.indent_text(quote_markdown)

        children_markdown = await context.render_children_with_additional_indent(1)

        if children_markdown:
            context.markdown_result = f"{quote_markdown}\n{children_markdown}"
        else:
            context.markdown_result = quote_markdown

    async def _convert_quote_to_markdown(self, block: Block) -> str | None:
        if not block.quote or not block.quote.rich_text:
            return None

        return await self._rich_text_markdown_converter.to_markdown(
            block.quote.rich_text
        )
