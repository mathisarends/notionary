from typing import override

from notionary.blocks.rich_text.rich_text_markdown_converter import (
    RichTextToMarkdownConverter,
)
from notionary.blocks.schemas import Block, BlockType
from notionary.page.content.renderer.context import MarkdownRenderingContext
from notionary.page.content.renderer.renderers.base import BlockRenderer


class NumberedListRenderer(BlockRenderer):
    # Placeholder for numbered list fixer (post processing)
    NUMBERED_LIST_PLACEHOLDER = "__NUM__"

    def __init__(self, rich_text_markdown_converter: RichTextToMarkdownConverter | None = None) -> None:
        super().__init__()
        self._rich_text_markdown_converter = rich_text_markdown_converter or RichTextToMarkdownConverter()

    @override
    def _can_handle(self, block: Block) -> bool:
        return block.type == BlockType.NUMBERED_LIST_ITEM

    @override
    async def _process(self, context: MarkdownRenderingContext) -> None:
        list_item_data = context.block.numbered_list_item
        rich_text = list_item_data.rich_text if list_item_data else []
        content = await self._rich_text_markdown_converter.to_markdown(rich_text)

        item_line = context.indent_text(f"{self.NUMBERED_LIST_PLACEHOLDER}. {content}")

        children_markdown = await context.render_children_with_additional_indent(1)

        if children_markdown:
            context.markdown_result = f"{item_line}\n{children_markdown}"
        else:
            context.markdown_result = item_line
