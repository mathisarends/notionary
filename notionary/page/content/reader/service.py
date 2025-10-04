from notionary.blocks.registry.service import BlockRegistry
from notionary.blocks.schemas import Block
from notionary.page.content.reader.context import BlockRenderingContext
from notionary.page.content.reader.handler import (
    ColumnListRenderer,
    ColumnRenderer,
    LineRenderer,
    NumberedListRenderer,
    ToggleableHeadingRenderer,
    ToggleRenderer,
)
from notionary.utils.mixins.logging import LoggingMixin


class NotionToMarkdownConverter(LoggingMixin):
    def __init__(
        self,
        block_registry: BlockRegistry,
        toggle_handler: ToggleRenderer | None = None,
        toggleable_heading_handler: ToggleableHeadingRenderer | None = None,
        column_list_handler: ColumnListRenderer | None = None,
        column_handler: ColumnRenderer | None = None,
        numbered_list_handler: NumberedListRenderer | None = None,
        regular_handler: LineRenderer | None = None,
    ) -> None:
        self._block_registry = block_registry

        self._toggle_handler = toggle_handler
        self._toggleable_heading_handler = toggleable_heading_handler
        self._column_list_handler = column_list_handler
        self._column_handler = column_handler
        self._numbered_list_handler = numbered_list_handler
        self._regular_handler = regular_handler

        self._setup_handler_chain()

    async def convert_to_markdown(self, blocks: list[Block]) -> str:
        return await self._convert_blocks_to_markdown(blocks, indent_level=0)

    def _setup_handler_chain(self) -> None:
        toggle_handler = self._toggle_handler or ToggleRenderer()
        toggleable_heading_handler = self._toggleable_heading_handler or ToggleableHeadingRenderer()
        column_list_handler = self._column_list_handler or ColumnListRenderer()
        column_handler = self._column_handler or ColumnRenderer()
        numbered_list_handler = self._numbered_list_handler or NumberedListRenderer()
        regular_handler = self._regular_handler or LineRenderer()

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
