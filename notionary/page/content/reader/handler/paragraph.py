from typing import override

from notionary.blocks.mappings.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.blocks.schemas import Block, BlockType
from notionary.page.content.reader.context import BlockRenderingContext
from notionary.page.content.reader.handler.base import BlockRenderer


class ParagraphRenderer(BlockRenderer):
    def __init__(self, rich_text_markdown_converter: RichTextToMarkdownConverter | None = None) -> None:
        super().__init__()
        self._rich_text_markdown_converter = rich_text_markdown_converter or RichTextToMarkdownConverter()

    @override
    def _can_handle(self, block: Block) -> bool:
        return block.type == BlockType.PARAGRAPH

    @override
    async def _process(self, context: BlockRenderingContext) -> None:
        markdown = await self._convert_paragraph_to_markdown(context.block)

        if not markdown:
            context.markdown_result = ""
            return

        if context.indent_level > 0:
            markdown = context.indent_text(markdown)

        # Process children if they exist
        children_markdown = await context.render_children_with_additional_indent(1)

        if children_markdown:
            context.markdown_result = f"{markdown}\n{children_markdown}"
        else:
            context.markdown_result = markdown

    async def _convert_paragraph_to_markdown(self, block: Block) -> str | None:
        if not block.paragraph or not block.paragraph.rich_text:
            return None

        return await self._rich_text_markdown_converter.to_markdown(block.paragraph.rich_text)
