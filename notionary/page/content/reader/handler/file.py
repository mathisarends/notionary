from typing import override

from notionary.blocks.mappings.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.blocks.schemas import Block, BlockType
from notionary.page.content.reader.context import BlockRenderingContext
from notionary.page.content.reader.handler.base import BlockRenderer


class FileRenderer(BlockRenderer):
    def __init__(self, rich_text_markdown_converter: RichTextToMarkdownConverter | None = None) -> None:
        super().__init__()
        self._rich_text_markdown_converter = rich_text_markdown_converter or RichTextToMarkdownConverter()

    @override
    def _can_handle(self, context: BlockRenderingContext) -> bool:
        return context.block.type == BlockType.FILE

    @override
    async def _process(self, context: BlockRenderingContext) -> None:
        url = self._extract_file_url(context.block)
        name = self._extract_file_name(context.block)
        caption = await self._extract_file_caption(context.block)

        if not url:
            context.markdown_result = ""
            return

        link_text = caption or name or "file"
        file_markdown = f"[{link_text}]({url})"

        if context.indent_level > 0:
            file_markdown = context.indent_text(file_markdown)

        children_markdown = await context.render_children_with_additional_indent(1)

        if children_markdown:
            context.markdown_result = f"{file_markdown}\n{children_markdown}"
        else:
            context.markdown_result = file_markdown

    def _extract_file_url(self, block: Block) -> str:
        if not block.file:
            return ""

        if hasattr(block.file, "external") and block.file.external:
            return block.file.external.url or ""
        elif hasattr(block.file, "file") and block.file.file:
            return block.file.file.url or ""

        return ""

    def _extract_file_name(self, block: Block) -> str:
        if not block.file:
            return ""

        if hasattr(block.file, "name"):
            return block.file.name or ""

        return ""

    async def _extract_file_caption(self, block: Block) -> str:
        caption_rich_text = []
        if block.file and block.file.caption:
            caption_rich_text = block.file.caption

        return await self._rich_text_markdown_converter.to_markdown(caption_rich_text)
