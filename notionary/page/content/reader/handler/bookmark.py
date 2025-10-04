from typing import override

from notionary.blocks.mappings.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.blocks.schemas import Block, BlockType
from notionary.page.content.reader.context import BlockRenderingContext
from notionary.page.content.reader.handler.base import BlockRenderer


class BookmarkRenderer(BlockRenderer):
    def __init__(self, rich_text_markdown_converter: RichTextToMarkdownConverter | None = None) -> None:
        super().__init__()
        self._rich_text_markdown_converter = rich_text_markdown_converter or RichTextToMarkdownConverter()

    @override
    def _can_handle(self, context: BlockRenderingContext) -> bool:
        return context.block.type == BlockType.BOOKMARK

    @override
    async def _process(self, context: BlockRenderingContext) -> None:
        url = self._extract_bookmark_url(context.block)
        caption = await self._extract_bookmark_caption(context.block)

        if not url:
            context.markdown_result = ""
            context.was_processed = True
            return

        bookmark_markdown = f"[{caption}]({url})" if caption else f"<{url}>"

        if context.indent_level > 0:
            bookmark_markdown = context.indent_text(bookmark_markdown)

        children_markdown = await context.render_children_with_additional_indent(1)

        if children_markdown:
            context.markdown_result = f"{bookmark_markdown}\n{children_markdown}"
        else:
            context.markdown_result = bookmark_markdown

        context.was_processed = True

    def _extract_bookmark_url(self, block: Block) -> str:
        if not block.bookmark:
            return ""
        return block.bookmark.url or ""

    async def _extract_bookmark_caption(self, block: Block) -> str:
        caption_rich_text = []
        if block.bookmark and block.bookmark.caption:
            caption_rich_text = block.bookmark.caption

        return await self._rich_text_markdown_converter.to_markdown(caption_rich_text)
