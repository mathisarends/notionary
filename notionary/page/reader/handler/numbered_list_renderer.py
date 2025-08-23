from notionary.blocks.models import Block, BlockType
from notionary.blocks.registry.block_registry import BlockRegistry
from notionary.page.reader.handler.base_block_renderer import BlockHandler
from notionary.page.reader.handler.block_rendering_context import BlockRenderingContext


class NumberedListRenderer(BlockHandler):
    """Handles numbered list items with sequential numbering."""

    def _can_handle(self, context: BlockRenderingContext) -> bool:
        """Check if this is a numbered list item."""
        return (
            context.block.type == BlockType.NUMBERED_LIST_ITEM
            and context.block.numbered_list_item is not None
        )

    async def _process(self, context: BlockRenderingContext) -> None:
        """Process numbered list item with sequential numbering."""
        if context.all_blocks is None or context.current_block_index is None:
            await self._process_single_item(context, 1)
            return

        items, blocks_to_skip = self._collect_numbered_list_items(context)

        markdown_parts = []
        for i, item_context in enumerate(items, 1):
            item_markdown = await self._process_single_item(item_context, i)
            if item_markdown:
                markdown_parts.append(item_markdown)

        # Set result and mark how many blocks to skip
        if markdown_parts:
            context.markdown_result = "\n".join(markdown_parts)
            context.was_processed = True
            context.blocks_consumed = blocks_to_skip

    def _collect_numbered_list_items(
        self, context: BlockRenderingContext
    ) -> tuple[list[BlockRenderingContext], int]:
        """Collect all consecutive numbered list items starting from current position."""
        items = []
        current_index = context.current_block_index
        all_blocks = context.all_blocks

        # Start with current block
        items.append(context)
        blocks_processed = 1

        # Look ahead for more numbered list items
        for i in range(current_index + 1, len(all_blocks)):
            block = all_blocks[i]

            # Check if it's a numbered list item
            if (
                block.type == BlockType.NUMBERED_LIST_ITEM
                and block.numbered_list_item is not None
            ):

                # Create context for this item
                item_context = BlockRenderingContext(
                    block=block,
                    indent_level=context.indent_level,
                    block_registry=context.block_registry,
                    convert_children_callback=context.convert_children_callback,
                )
                items.append(item_context)
                blocks_processed += 1
            else:
                # Not a numbered list item - stop collecting
                break

        return items, blocks_processed

    async def _process_single_item(
        self, context: BlockRenderingContext, number: int
    ) -> str:
        """Process a single numbered list item with the given number."""
        from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter

        rich_text = context.block.numbered_list_item.rich_text
        content = await TextInlineFormatter.extract_text_with_formatting(rich_text)

        # Apply indentation
        indent = "  " * context.indent_level
        return f"{indent}{number}. {content}"
