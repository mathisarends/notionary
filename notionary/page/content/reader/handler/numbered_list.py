from typing import override

from notionary.blocks.mappings.rich_text.rich_text_markdown_converter import (
    RichTextToMarkdownConverter,
)
from notionary.blocks.schemas import Block, BlockType
from notionary.page.content.reader.context import BlockRenderingContext
from notionary.page.content.reader.handler.base import BlockRenderer


class NumberedListRenderer(BlockRenderer):
    def __init__(self, rich_text_markdown_converter: RichTextToMarkdownConverter | None = None) -> None:
        super().__init__()
        self._rich_text_markdown_converter = rich_text_markdown_converter or RichTextToMarkdownConverter()

    @override
    def _can_handle(self, block: Block) -> bool:
        return block.type == BlockType.NUMBERED_LIST_ITEM

    @override
    async def _process(self, context: BlockRenderingContext) -> None:
        if self._is_standalone_item(context):
            await self._process_standalone_item(context)
            return

        await self._process_list_group(context)

    def _is_standalone_item(self, context: BlockRenderingContext) -> bool:
        return context.all_blocks is None or context.current_block_index is None

    async def _process_standalone_item(self, context: BlockRenderingContext) -> None:
        item_markdown = await self._render_list_item(context, number=1)
        context.markdown_result = item_markdown

    async def _process_list_group(self, context: BlockRenderingContext) -> None:
        items = self._collect_consecutive_list_items(context)
        markdown_parts = await self._render_all_items(items)

        if markdown_parts:
            context.markdown_result = "\n".join(markdown_parts)
            context.blocks_consumed = len(items) - 1

    def _collect_consecutive_list_items(self, context: BlockRenderingContext) -> list[BlockRenderingContext]:
        items = [context]

        if context.current_block_index is None or context.all_blocks is None:
            return items

        next_index = context.current_block_index + 1
        while next_index < len(context.all_blocks):
            block = context.all_blocks[next_index]

            if block.type != BlockType.NUMBERED_LIST_ITEM:
                break

            items.append(
                BlockRenderingContext(
                    block=block,
                    indent_level=context.indent_level,
                    convert_children_callback=context.convert_children_callback,
                )
            )
            next_index += 1

        return items

    async def _render_all_items(self, items: list[BlockRenderingContext]) -> list[str]:
        markdown_parts = []

        for number, item_context in enumerate(items, start=1):
            item_markdown = await self._render_list_item(item_context, number)
            if item_markdown:
                markdown_parts.append(item_markdown)

        return markdown_parts

    async def _render_list_item(self, context: BlockRenderingContext, number: int) -> str:
        """Renders a single list item, including its text and any nested child blocks."""
        # Render the item's own text
        list_item_data = context.block.numbered_list_item
        rich_text = list_item_data.rich_text if list_item_data else []
        content = await self._rich_text_markdown_converter.to_markdown(rich_text)

        # Create the item line with proper indentation
        item_line = context.indent_text(f"{number}. {content}")

        # Render children with additional indent
        children_markdown = await context.render_children_with_additional_indent(1)

        # Combine the item line with its children
        if children_markdown:
            return f"{item_line}\n{children_markdown}"

        return item_line
