from typing import override

from notionary.blocks.mappings.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.blocks.schemas import Block, BlockType
from notionary.page.content.reader.context import BlockRenderingContext
from notionary.page.content.reader.handler.base import BlockRenderer


class ImageRenderer(BlockRenderer):
    def __init__(self, rich_text_markdown_converter: RichTextToMarkdownConverter | None = None) -> None:
        super().__init__()
        self._rich_text_markdown_converter = rich_text_markdown_converter or RichTextToMarkdownConverter()

    @override
    def _can_handle(self, block: Block) -> bool:
        return block.type == BlockType.IMAGE

    @override
    async def _process(self, context: BlockRenderingContext) -> None:
        url = self._extract_image_url(context.block)
        caption = await self._extract_image_caption(context.block)

        if not url:
            context.markdown_result = ""
            return

        alt_text = caption or "image"
        image_markdown = f"![{alt_text}]({url})"

        if context.indent_level > 0:
            image_markdown = context.indent_text(image_markdown)

        children_markdown = await context.render_children_with_additional_indent(1)

        if children_markdown:
            context.markdown_result = f"{image_markdown}\n{children_markdown}"
        else:
            context.markdown_result = image_markdown

    def _extract_image_url(self, block: Block) -> str:
        if not block.image:
            return ""

        if hasattr(block.image, "external") and block.image.external:
            return block.image.external.url or ""
        elif hasattr(block.image, "file") and block.image.file:
            return block.image.file.url or ""

        return ""

    async def _extract_image_caption(self, block: Block) -> str:
        caption_rich_text = []
        if block.image and block.image.caption:
            caption_rich_text = block.image.caption

        return await self._rich_text_markdown_converter.to_markdown(caption_rich_text)
