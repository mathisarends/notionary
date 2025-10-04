from typing import override

from notionary.blocks.mappings.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.blocks.schemas import Block, BlockType
from notionary.page.content.reader.context import BlockRenderingContext
from notionary.page.content.reader.handler.base import BlockRenderer


class VideoRenderer(BlockRenderer):
    def __init__(self, rich_text_markdown_converter: RichTextToMarkdownConverter | None = None) -> None:
        super().__init__()
        self._rich_text_markdown_converter = rich_text_markdown_converter or RichTextToMarkdownConverter()

    @override
    def _can_handle(self, context: BlockRenderingContext) -> bool:
        return context.block.type == BlockType.VIDEO

    @override
    async def _process(self, context: BlockRenderingContext) -> None:
        url = self._extract_video_url(context.block)
        caption = await self._extract_video_caption(context.block)

        if not url:
            context.markdown_result = ""
            context.was_processed = True
            return

        alt_text = caption or "video"
        video_markdown = f"![{alt_text}]({url})"

        if context.indent_level > 0:
            video_markdown = context.indent_text(video_markdown)

        children_markdown = await context.render_children_with_additional_indent(1)

        if children_markdown:
            context.markdown_result = f"{video_markdown}\n{children_markdown}"
        else:
            context.markdown_result = video_markdown

        context.was_processed = True

    def _extract_video_url(self, block: Block) -> str:
        if not block.video:
            return ""

        if hasattr(block.video, "external") and block.video.external:
            return block.video.external.url or ""
        elif hasattr(block.video, "file") and block.video.file:
            return block.video.file.url or ""

        return ""

    async def _extract_video_caption(self, block: Block) -> str:
        caption_rich_text = []
        if block.video and block.video.caption:
            caption_rich_text = block.video.caption

        return await self._rich_text_markdown_converter.to_markdown(caption_rich_text)
