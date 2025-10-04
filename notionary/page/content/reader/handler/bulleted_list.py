from typing import override

from notionary.blocks.mappings.bulleted_list import BulletedListMapper
from notionary.blocks.mappings.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.blocks.schemas import Block
from notionary.page.content.reader.context import BlockRenderingContext
from notionary.page.content.reader.handler.base import BlockRenderer


class BulletedListRenderer(BlockRenderer):
    BULLET_MARKER = "- "

    def __init__(self, rich_text_markdown_converter: RichTextToMarkdownConverter | None = None) -> None:
        super().__init__()
        self._rich_text_markdown_converter = rich_text_markdown_converter or RichTextToMarkdownConverter()

    @override
    def _can_handle(self, context: BlockRenderingContext) -> bool:
        return BulletedListMapper.match_notion(context.block)

    @override
    async def _process(self, context: BlockRenderingContext) -> None:
        markdown = await self._convert_bulleted_list_to_markdown(context.block)

        if not markdown:
            context.markdown_result = ""
            context.was_processed = True
            return

        list_item_markdown = f"{self.BULLET_MARKER}{markdown}"

        if context.indent_level > 0:
            list_item_markdown = context.indent_text(list_item_markdown)

        children_markdown = await context.render_children_with_additional_indent(1)

        if children_markdown:
            context.markdown_result = f"{list_item_markdown}\n{children_markdown}"
        else:
            context.markdown_result = list_item_markdown

        context.was_processed = True

    async def _convert_bulleted_list_to_markdown(self, block: Block) -> str | None:
        if not block.bulleted_list_item or not block.bulleted_list_item.rich_text:
            return None

        return await self._rich_text_markdown_converter.to_markdown(block.bulleted_list_item.rich_text)
