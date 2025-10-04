from typing import override

from notionary.blocks.enums import BlockType
from notionary.blocks.mappings.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.blocks.schemas import Block
from notionary.page.content.reader.context import BlockRenderingContext
from notionary.page.content.reader.handler.base import BlockRenderer


class CodeRenderer(BlockRenderer):
    CODE_FENCE = "```"

    def __init__(self, rich_text_markdown_converter: RichTextToMarkdownConverter | None = None) -> None:
        super().__init__()
        self._rich_text_markdown_converter = rich_text_markdown_converter or RichTextToMarkdownConverter()

    @override
    def _can_handle(self, context: BlockRenderingContext) -> bool:
        block = context.block
        return block.type == BlockType.CODE

    @override
    async def _process(self, context: BlockRenderingContext) -> None:
        language = self._extract_code_language(context.block)
        code_content = await self._extract_code_content(context.block)
        caption = await self._extract_code_caption(context.block)

        if not code_content:
            context.markdown_result = ""
            return

        # Build code block
        code_start = f"{self.CODE_FENCE}{language}"
        code_end = self.CODE_FENCE
        code_markdown = f"{code_start}\n{code_content}\n{code_end}"

        # Add caption if present
        if caption:
            code_markdown = f"{code_markdown}\n*{caption}*"

        if context.indent_level > 0:
            code_markdown = context.indent_text(code_markdown)

        children_markdown = await context.render_children_with_additional_indent(1)

        if children_markdown:
            context.markdown_result = f"{code_markdown}\n{children_markdown}"
        else:
            context.markdown_result = code_markdown

    def _extract_code_language(self, block: Block) -> str:
        if not block.code or not block.code.language:
            return ""
        return block.code.language.value

    async def _extract_code_content(self, block: Block) -> str:
        if not block.code or not block.code.rich_text:
            return ""
        return await self._rich_text_markdown_converter.to_markdown(block.code.rich_text)

    async def _extract_code_caption(self, block: Block) -> str:
        caption_rich_text = []
        if block.code and block.code.caption:
            caption_rich_text = block.code.caption

        return await self._rich_text_markdown_converter.to_markdown(caption_rich_text)
