from typing import override

from notionary.blocks.enums import BlockType
from notionary.blocks.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.blocks.schemas import Block
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.base import BlockRenderer


class ToggleRenderer(BlockRenderer):
    TOGGLE_DELIMITER = "+++"

    def __init__(self, rich_text_markdown_converter: RichTextToMarkdownConverter | None = None) -> None:
        super().__init__()
        self._rich_text_markdown_converter = rich_text_markdown_converter or RichTextToMarkdownConverter()

    @override
    def _can_handle(self, block: Block) -> bool:
        return block.type == BlockType.TOGGLE

    @override
    async def _process(self, context: MarkdownRenderingContext) -> None:
        toggle_title = await self._extract_toggle_title(context.block)

        if not toggle_title:
            return

        toggle_start = f"{self.TOGGLE_DELIMITER} {toggle_title}"

        if context.indent_level > 0:
            toggle_start = context.indent_text(toggle_start)

        children_markdown = await context.render_children()

        toggle_end = self.TOGGLE_DELIMITER
        if context.indent_level > 0:
            toggle_end = context.indent_text(toggle_end)

        if children_markdown:
            context.markdown_result = f"{toggle_start}\n{children_markdown}\n{toggle_end}"
        else:
            context.markdown_result = f"{toggle_start}\n{toggle_end}"

    async def _extract_toggle_title(self, block: Block) -> str:
        if not block.toggle or not block.toggle.rich_text:
            return ""

        rich_text_title = block.toggle.rich_text
        return await self._rich_text_markdown_converter.to_markdown(rich_text_title)
