from typing import override

from notionary.blocks.mappings.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.blocks.schemas import Block, BlockType
from notionary.page.content.reader.context import BlockRenderingContext
from notionary.page.content.reader.handler.base import BlockRenderer


class ToggleableHeadingRenderer(BlockRenderer):
    TOGGLE_DELIMITER = ":::"

    def __init__(self, rich_text_markdown_converter: RichTextToMarkdownConverter | None = None) -> None:
        super().__init__()
        self._rich_text_markdown_converter = rich_text_markdown_converter or RichTextToMarkdownConverter()

    @override
    def _can_handle(self, context: BlockRenderingContext) -> bool:
        block = context.block

        if block.type == BlockType.HEADING_1:
            return block.heading_1.is_toggleable
        if block.type == BlockType.HEADING_2:
            return block.heading_2.is_toggleable
        if block.type == BlockType.HEADING_3:
            return block.heading_3.is_toggleable

    @override
    async def _process(self, context: BlockRenderingContext) -> None:
        level = self._get_heading_level(context.block)
        title = await self._get_heading_title(context.block)

        if not title or level == 0:
            return

        prefix = self.TOGGLE_DELIMITER + " " + ("#" * level)
        heading_start = f"{prefix} {title}"

        if context.indent_level > 0:
            heading_start = context.indent_text(heading_start)

        children_markdown = await context.render_children()

        heading_end = self.TOGGLE_DELIMITER
        if context.indent_level > 0:
            heading_end = context.indent_text(heading_end)

        if children_markdown:
            context.markdown_result = f"{heading_start}\n{children_markdown}\n{heading_end}"
        else:
            context.markdown_result = f"{heading_start}\n{heading_end}"

    def _get_heading_level(self, block: Block) -> int:
        if block.type == BlockType.HEADING_1:
            return 1
        elif block.type == BlockType.HEADING_2:
            return 2
        elif block.type == BlockType.HEADING_3:
            return 3
        else:
            return 0

    async def _get_heading_title(self, block: Block) -> str:
        if block.type == BlockType.HEADING_1:
            heading_content = block.heading_1
        elif block.type == BlockType.HEADING_2:
            heading_content = block.heading_2
        elif block.type == BlockType.HEADING_3:
            heading_content = block.heading_3
        else:
            return ""

        if not heading_content or not heading_content.rich_text:
            return ""

        return await self._rich_text_markdown_converter.to_markdown(heading_content.rich_text)
