from notionary.blocks.models import BlockCreateRequest
from notionary.blocks.registry.block_registry import BlockRegistry
from notionary.page.writer.handler import (
    CodeHandler,
    ColumnHandler,
    ColumnListHandler,
    EquationHandler,
    LineProcessingContext,
    ParentBlockContext,
    RegularLineHandler,
    TableHandler,
    ToggleableHeadingHandler,
    ToggleHandler,
)
from notionary.page.writer.markdown_to_notion_formatting_post_processor import (
    MarkdownToNotionFormattingPostProcessor,
)
from notionary.page.writer.notion_text_length_processor import (
    NotionTextLengthProcessor,
)


class MarkdownToNotionConverter:
    """Converts Markdown text to Notion API block format with unified stack-based processing."""

    def __init__(self, block_registry: BlockRegistry) -> None:
        self._block_registry = block_registry
        self._formatting_post_processor = MarkdownToNotionFormattingPostProcessor()
        self._text_length_post_processor = NotionTextLengthProcessor()

        self._setup_handler_chain()

    def _setup_handler_chain(self) -> None:
        code_handler = CodeHandler()
        equation_handler = EquationHandler()
        table_handler = TableHandler()
        column_list_handler = ColumnListHandler()
        column_handler = ColumnHandler()
        toggle_handler = ToggleHandler()
        toggleable_heading_handler = ToggleableHeadingHandler()
        regular_handler = RegularLineHandler()

        # register more specific elements first
        code_handler.set_next(equation_handler).set_next(table_handler).set_next(
            column_list_handler
        ).set_next(column_handler).set_next(toggleable_heading_handler).set_next(
            toggle_handler
        ).set_next(
            regular_handler
        )

        self._handler_chain = code_handler

    async def convert(self, markdown_text: str) -> list[BlockCreateRequest]:
        if not markdown_text.strip():
            return []

        all_blocks = await self.process_lines(markdown_text)

        # Apply formatting post-processing (empty paragraphs)
        all_blocks = self._formatting_post_processor.process(all_blocks)

        # Apply text length post-processing (truncation)
        all_blocks = self._text_length_post_processor.process(all_blocks)

        return all_blocks

    async def process_lines(self, text: str) -> list[BlockCreateRequest]:
        lines = text.split("\n")
        result_blocks: list[BlockCreateRequest] = []
        parent_stack: list[ParentBlockContext] = []

        i = 0
        while i < len(lines):
            line = lines[i]

            context = LineProcessingContext(
                line=line,
                result_blocks=result_blocks,
                parent_stack=parent_stack,
                block_registry=self._block_registry,
                all_lines=lines,
                current_line_index=i,
                lines_consumed=0,
            )

            await self._handler_chain.handle(context)

            # Skip consumed lines
            i += 1 + context.lines_consumed

            if context.should_continue:
                continue

        return result_blocks
