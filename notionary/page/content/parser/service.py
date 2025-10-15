from notionary.blocks.schemas import BlockCreatePayload
from notionary.page.content.parser.parsers import (
    BlockParsingContext,
    ParentBlockContext,
)
from notionary.page.content.parser.parsers.base import LineParser
from notionary.page.content.parser.post_processing.service import BlockPostProcessor
from notionary.page.content.parser.pre_processsing.service import MarkdownPreProcessor
from notionary.utils.decorators import time_execution_async
from notionary.utils.mixins.logging import LoggingMixin


class MarkdownToNotionConverter(LoggingMixin):
    def __init__(
        self, line_parser: LineParser, pre_processor: MarkdownPreProcessor, post_processor: BlockPostProcessor
    ) -> None:
        self._line_parser = line_parser
        self._pre_processor = pre_processor
        self._post_processor = post_processor

    @time_execution_async()
    async def convert(self, markdown_text: str) -> list[BlockCreatePayload]:
        if not markdown_text:
            return []

        markdown_text = self._pre_processor.process(markdown_text)
        all_blocks = await self._process_lines(markdown_text)
        all_blocks = self._post_processor.process(all_blocks)

        return all_blocks

    async def _process_lines(self, text: str) -> list[BlockCreatePayload]:
        lines = text.split("\n")
        result_blocks: list[BlockCreatePayload] = []
        parent_stack: list[ParentBlockContext] = []

        current_line_index = 0
        previous_line_was_empty = False

        while current_line_index < len(lines):
            line = lines[current_line_index]

            context = self._create_line_processing_context(
                line=line,
                lines=lines,
                line_index=current_line_index,
                result_blocks=result_blocks,
                parent_stack=parent_stack,
                is_previous_line_empty=previous_line_was_empty,
            )

            await self._line_parser.handle(context)
            previous_line_was_empty = self._is_processed_line_empty(line)

            current_line_index += 1 + context.lines_consumed

        return result_blocks

    def _create_line_processing_context(
        self,
        line: str,
        lines: list[str],
        line_index: int,
        result_blocks: list[BlockCreatePayload],
        parent_stack: list[ParentBlockContext],
        is_previous_line_empty: bool = False,
    ) -> BlockParsingContext:
        return BlockParsingContext(
            line=line,
            result_blocks=result_blocks,
            parent_stack=parent_stack,
            parse_children_callback=self._process_lines,
            all_lines=lines,
            current_line_index=line_index,
            lines_consumed=0,
            is_previous_line_empty=is_previous_line_empty,
        )

    def _is_processed_line_empty(self, line: str) -> bool:
        return line.strip() == ""
