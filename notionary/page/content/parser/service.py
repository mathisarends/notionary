from notionary.blocks.registry.service import BlockRegistry
from notionary.blocks.schemas import BlockCreatePayload
from notionary.page.content.parser.parsers import (
    CodeParser,
    ColumnListParser,
    ColumnParser,
    EquationParser,
    LineProcessingContext,
    ParentBlockContext,
    RegularLineParser,
    TableParser,
    ToggleableHeadingParser,
    ToggleParser,
)
from notionary.page.content.parser.pre_processsing.text_length import (
    NotionTextLengthProcessor,
)
from notionary.utils.mixins.logging import LoggingMixin


class MarkdownToNotionConverter(LoggingMixin):
    def __init__(
        self,
        block_registry: BlockRegistry,
        code_parser: CodeParser | None = None,
        equation_parser: EquationParser | None = None,
        table_parser: TableParser | None = None,
        column_list_parser: ColumnListParser | None = None,
        column_parser: ColumnParser | None = None,
        toggle_parser: ToggleParser | None = None,
        toggleable_heading_parser: ToggleableHeadingParser | None = None,
        regular_line_parser: RegularLineParser | None = None,
    ) -> None:
        self._block_registry = block_registry
        self._text_length_post_processor = NotionTextLengthProcessor()

        self._code_parser = code_parser
        self._equation_parser = equation_parser
        self._table_parser = table_parser
        self._column_list_parser = column_list_parser
        self._column_parser = column_parser
        self._toggle_parser = toggle_parser
        self._toggleable_heading_parser = toggleable_heading_parser
        self._regular_line_parser = regular_line_parser

        self._setup_handler_chain()

    def _setup_handler_chain(self) -> None:
        code_parser = self._code_parser or CodeParser()
        equation_parser = self._equation_parser or EquationParser()
        table_parser = self._table_parser or TableParser()
        column_list_parser = self._column_list_parser or ColumnListParser()
        column_parser = self._column_parser or ColumnParser()
        toggle_parser = self._toggle_parser or ToggleParser()
        toggleable_heading_parser = self._toggleable_heading_parser or ToggleableHeadingParser()
        regular_line_parser = self._regular_line_parser or RegularLineParser()

        code_parser.set_next(equation_parser).set_next(table_parser).set_next(column_parser).set_next(
            column_list_parser
        ).set_next(toggleable_heading_parser).set_next(toggle_parser).set_next(regular_line_parser)

        self._handler_chain = code_parser

    async def convert(self, markdown_text: str) -> list[BlockCreatePayload]:
        if not markdown_text.strip():
            return []

        all_blocks = await self.process_lines(markdown_text)

        all_blocks = self._text_length_post_processor.process(all_blocks)

        return all_blocks

    async def process_lines(self, text: str) -> list[BlockCreatePayload]:
        lines = text.split("\n")
        result_blocks: list[BlockCreatePayload] = []
        parent_stack: list[ParentBlockContext] = []

        current_line_index = 0
        while current_line_index < len(lines):
            line = lines[current_line_index]

            context = self._create_line_processing_context(
                line=line,
                lines=lines,
                line_index=current_line_index,
                result_blocks=result_blocks,
                parent_stack=parent_stack,
            )

            await self._handler_chain.handle(context)

            current_line_index += 1 + context.lines_consumed

            if context.should_continue:
                continue

        return result_blocks

    def _create_line_processing_context(
        self,
        line: str,
        lines: list[str],
        line_index: int,
        result_blocks: list[BlockCreatePayload],
        parent_stack: list[ParentBlockContext],
    ) -> LineProcessingContext:
        return LineProcessingContext(
            line=line,
            result_blocks=result_blocks,
            parent_stack=parent_stack,
            block_registry=self._block_registry,
            all_lines=lines,
            current_line_index=line_index,
            lines_consumed=0,
        )
