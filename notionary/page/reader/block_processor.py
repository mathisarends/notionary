from notionary.blocks.block_models import Block
from notionary.blocks.registry.block_registry import BlockRegistry
from notionary.page.reader.block_handler import BlockHandler
from notionary.page.reader.context import BlockProcessingContext
from notionary.page.reader.column_block_handler import ColumnBlockHandler
from notionary.page.reader.column_list_block_handler import ColumnListBlockHandler
from notionary.page.reader.regular_block_handler import RegularBlockHandler
from notionary.page.reader.toggle_block_handler import ToggleBlockHandler
from notionary.page.reader.toggleable_heading_block_handler import ToggleableHeadingBlockHandler


class BlockProcessor:
    """Processes Notion blocks using chain of responsibility pattern."""

    def __init__(self, block_registry: BlockRegistry):
        self.block_registry = block_registry
        self._setup_handler_chain()

    def _setup_handler_chain(self) -> None:
        """Setup the chain of handlers in priority order."""
        toggle_handler = ToggleBlockHandler()
        toggleable_heading_handler = ToggleableHeadingBlockHandler()
        column_list_handler = ColumnListBlockHandler()
        column_handler = ColumnBlockHandler()
        regular_handler = RegularBlockHandler()

        # Chain handlers - most specific first
        toggle_handler.set_next(toggleable_heading_handler).set_next(
            column_list_handler
        ).set_next(column_handler).set_next(regular_handler)

        self._handler_chain = toggle_handler

    def convert_blocks_to_markdown(
        self, blocks: list[Block], indent_level: int = 0
    ) -> str:
        """Convert blocks to Markdown using the handler chain."""
        if not blocks:
            return ""

        markdown_parts = []

        for block in blocks:
            context = BlockProcessingContext(
                block=block,
                indent_level=indent_level,
                block_registry=self.block_registry,
            )

            self._handler_chain.handle(context)

            if context.was_processed and context.markdown_result:
                markdown_parts.append(context.markdown_result)

        separator = "\n\n" if indent_level == 0 else "\n"
        return separator.join(markdown_parts)
