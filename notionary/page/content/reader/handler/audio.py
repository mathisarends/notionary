from typing import override

from notionary.blocks.mappings.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.blocks.schemas import Block, BlockType
from notionary.page.content.reader.context import BlockRenderingContext
from notionary.page.content.reader.handler.base import BlockRenderer


class AudioRenderer(BlockRenderer):
    def __init__(self, rich_text_markdown_converter: RichTextToMarkdownConverter | None = None) -> None:
        super().__init__()
        self._rich_text_markdown_converter = rich_text_markdown_converter or RichTextToMarkdownConverter()

    @override
    def _can_handle(self, context: BlockRenderingContext) -> bool:
        return context.block.type == BlockType.AUDIO

    @override
    async def _process(self, context: BlockRenderingContext) -> None:
        url = self._extract_audio_url(context.block)
        caption = await self._extract_audio_caption(context.block)

        if not url:
            context.markdown_result = ""
            context.was_processed = True
            return

        alt_text = caption or "audio"
        audio_markdown = f"![{alt_text}]({url})"

        if context.indent_level > 0:
            audio_markdown = context.indent_text(audio_markdown)

        children_markdown = await context.render_children_with_additional_indent(1)

        if children_markdown:
            context.markdown_result = f"{audio_markdown}\n{children_markdown}"
        else:
            context.markdown_result = audio_markdown

        context.was_processed = True

    def _extract_audio_url(self, block: Block) -> str:
        if not block.audio:
            return ""

        if block.audio.external:
            return block.audio.external.url or ""
        elif block.audio.file:
            return block.audio.file.url or ""

        return ""

    async def _extract_audio_caption(self, block: Block) -> str:
        caption_rich_text = []
        if block.audio and block.audio.caption:
            caption_rich_text = block.audio.caption

        return await self._rich_text_markdown_converter.to_markdown(caption_rich_text)
