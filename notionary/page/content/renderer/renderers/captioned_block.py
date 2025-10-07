from abc import abstractmethod
from typing import override

from notionary.blocks.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.blocks.schemas import Block
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.base import BlockRenderer
from notionary.page.content.syntax.service import SyntaxRegistry


class CaptionedBlockRenderer(BlockRenderer):
    def __init__(
        self,
        syntax_registry: SyntaxRegistry | None = None,
        rich_text_markdown_converter: RichTextToMarkdownConverter | None = None,
    ) -> None:
        super().__init__(syntax_registry=syntax_registry)
        self._rich_text_markdown_converter = rich_text_markdown_converter or RichTextToMarkdownConverter()

    @abstractmethod
    async def _render_main_content(self, block: Block) -> str:
        raise NotImplementedError

    @override
    async def _process(self, context: MarkdownRenderingContext) -> None:
        main_content = await self._render_main_content(context.block)

        if not main_content:
            context.markdown_result = ""
            return

        caption_markdown = await self._render_caption(context.block)

        final_markdown = f"{main_content}{caption_markdown}"

        if context.indent_level > 0:
            final_markdown = context.indent_text(final_markdown)

        children_markdown = await context.render_children_with_additional_indent(1)

        if children_markdown:
            context.markdown_result = f"{final_markdown}\n{children_markdown}"
        else:
            context.markdown_result = final_markdown

    async def _render_caption(self, block: Block) -> str:
        block_data_object = getattr(block, block.type.value, None)

        if not block_data_object or not hasattr(block_data_object, "caption"):
            return ""

        caption_rich_text = getattr(block_data_object, "caption", [])
        if not caption_rich_text:
            return ""

        caption_markdown = await self._rich_text_markdown_converter.to_markdown(caption_rich_text)

        return f"\n[caption] {caption_markdown}"
