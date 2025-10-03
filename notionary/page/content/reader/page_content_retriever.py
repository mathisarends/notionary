from notionary.blocks.registry.block_registry import BlockRegistry
from notionary.blocks.schemas import Block
from notionary.page.content.reader.handler.block_rendering_context import BlockRenderingContext
from notionary.page.content.reader.handler.column_list_renderer import ColumnListRenderer
from notionary.page.content.reader.handler.column_renderer import ColumnRenderer
from notionary.page.content.reader.handler.line_renderer import LineRenderer
from notionary.page.content.reader.handler.numbered_list_renderer import NumberedListRenderer
from notionary.page.content.reader.handler.toggle_renderer import ToggleRenderer
from notionary.page.content.reader.handler.toggleable_heading_renderer import ToggleableHeadingRenderer
from notionary.utils.mixins.logging import LoggingMixin


class PageContentRetriever(LoggingMixin):
    def __init__(
        self,
        block_registry: BlockRegistry,
    ) -> None:
        self._block_registry = block_registry

        self._setup_handler_chain()

    async def convert_to_markdown(self, blocks: list[Block]) -> str:
        return await self._convert_blocks_to_markdown(blocks, indent_level=0)

    def _setup_handler_chain(self) -> None:
        toggle_handler = ToggleRenderer()
        toggleable_heading_handler = ToggleableHeadingRenderer()
        column_list_handler = ColumnListRenderer()
        column_handler = ColumnRenderer()
        numbered_list_handler = NumberedListRenderer()
        regular_handler = LineRenderer()

        # Chain handlers - most specific first
        toggle_handler.set_next(toggleable_heading_handler).set_next(column_list_handler).set_next(
            column_handler
        ).set_next(numbered_list_handler).set_next(regular_handler)

        self._handler_chain = toggle_handler

    async def _convert_blocks_to_markdown(self, blocks: list[Block], indent_level: int = 0) -> str:
        if not blocks:
            return ""

        markdown_parts = []
        i = 0

        while i < len(blocks):
            block = blocks[i]
            context = BlockRenderingContext(
                block=block,
                indent_level=indent_level,
                block_registry=self._block_registry,
                all_blocks=blocks,
                current_block_index=i,
                convert_children_callback=self._convert_blocks_to_markdown,
            )

            await self._handler_chain.handle(context)

            if context.was_processed and context.markdown_result:
                markdown_parts.append(context.markdown_result)

            # Skip additional blocks if they were consumed by batch processing
            i += max(1, context.blocks_consumed)

        separator = "\n\n" if indent_level == 0 else "\n"
        return separator.join(markdown_parts)
