from typing import override

from notionary.blocks.mappings.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.blocks.schemas import Block, BlockType
from notionary.page.content.reader.context import BlockRenderingContext
from notionary.page.content.reader.handler.base import BlockRenderer


class PdfRenderer(BlockRenderer):
    def __init__(self, rich_text_markdown_converter: RichTextToMarkdownConverter | None = None) -> None:
        super().__init__()
        self._rich_text_markdown_converter = rich_text_markdown_converter or RichTextToMarkdownConverter()

    @override
    def _can_handle(self, context: BlockRenderingContext) -> bool:
        return context.block.type == BlockType.PDF

    @override
    async def _process(self, context: BlockRenderingContext) -> None:
        url = self._extract_pdf_url(context.block)
        caption = await self._extract_pdf_caption(context.block)

        if not url:
            context.markdown_result = ""
            context.was_processed = True
            return

        link_text = caption or "PDF"
        pdf_markdown = f"[{link_text}]({url})"

        if context.indent_level > 0:
            pdf_markdown = context.indent_text(pdf_markdown)

        children_markdown = await context.render_children_with_additional_indent(1)

        if children_markdown:
            context.markdown_result = f"{pdf_markdown}\n{children_markdown}"
        else:
            context.markdown_result = pdf_markdown

        context.was_processed = True

    def _extract_pdf_url(self, block: Block) -> str:
        if not block.pdf:
            return ""

        if hasattr(block.pdf, "external") and block.pdf.external:
            return block.pdf.external.url or ""
        elif hasattr(block.pdf, "file") and block.pdf.file:
            return block.pdf.file.url or ""

        return ""

    async def _extract_pdf_caption(self, block: Block) -> str:
        caption_rich_text = []
        if block.pdf and block.pdf.caption:
            caption_rich_text = block.pdf.caption

        return await self._rich_text_markdown_converter.to_markdown(caption_rich_text)
