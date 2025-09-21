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
from notionary.page.writer.notion_text_length_processor import (
    NotionTextLengthProcessor,
)
from notionary.util.logging_mixin import LoggingMixin


class HandlerOrderValidationError(RuntimeError):
    """Raised when handler chain order is incorrect."""

    pass


class MarkdownToNotionConverter(LoggingMixin):
    """Converts Markdown text to Notion API block format with unified stack-based processing."""

    def __init__(self, block_registry: BlockRegistry) -> None:
        self._block_registry = block_registry
        self._text_length_post_processor = NotionTextLengthProcessor()
        self._setup_handler_chain()

    async def convert(self, markdown_text: str) -> list[BlockCreateRequest]:
        if not markdown_text.strip():
            return []

        all_blocks = await self.process_lines(markdown_text)

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

    def _setup_handler_chain(self) -> None:
        code_handler = CodeHandler()
        equation_handler = EquationHandler()
        table_handler = TableHandler()
        column_list_handler = ColumnListHandler()
        column_handler = ColumnHandler()
        toggle_handler = ToggleHandler()
        toggleable_heading_handler = ToggleableHeadingHandler()
        regular_handler = RegularLineHandler()

        # Create handler chain
        code_handler.set_next(equation_handler).set_next(table_handler).set_next(column_handler).set_next(
            column_list_handler
        ).set_next(toggleable_heading_handler).set_next(toggle_handler).set_next(regular_handler)

        self._handler_chain = code_handler

        # Validate critical order - only log/error if something is wrong
        self._validate_handler_order(
            [
                code_handler,
                equation_handler,
                table_handler,
                column_handler,
                column_list_handler,
                toggleable_heading_handler,
                toggle_handler,
                regular_handler,
            ]
        )

    def _validate_handler_order(self, handlers) -> None:
        """Validate critical handler positioning rules - only warns/errors when needed."""
        handler_classes = [handler.__class__ for handler in handlers]

        # Critical: ColumnHandler MUST come before ColumnListHandler
        try:
            column_handler_pos = handler_classes.index(ColumnHandler)
            column_list_handler_pos = handler_classes.index(ColumnListHandler)

            if column_handler_pos >= column_list_handler_pos:
                error_msg = (
                    f"CRITICAL: ColumnHandler must come BEFORE ColumnListHandler. "
                    f"Current order: ColumnHandler at {column_handler_pos}, ColumnListHandler at {column_list_handler_pos}."
                    f"Fix: Move ColumnHandler before ColumnListHandler in _setup_handler_chain()"
                )
                self.logger.error(error_msg)
                raise HandlerOrderValidationError(error_msg)

        except ValueError as e:
            error_msg = f"Missing required handlers in chain: {e}"
            self.logger.error(error_msg)
            raise HandlerOrderValidationError(error_msg) from e

        # Critical: RegularLineHandler should be last (fallback)
        if handler_classes[-1] != RegularLineHandler:
            error_msg = (
                f"WARNING: RegularLineHandler should be last handler (fallback), "
                f"but {handler_classes[-1].__name__} is at the end"
            )
            self.logger.warning(error_msg)
