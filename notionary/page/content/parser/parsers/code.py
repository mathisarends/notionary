import re

from notionary.blocks.mappings.code import CodeMapper
from notionary.page.content.parser.parsers.base import (
    LineParser,
    LineProcessingContext,
)


class CodeParser(LineParser):
    def __init__(self) -> None:
        super().__init__()
        self._code_start_pattern = re.compile(r"^```(\w*)\s*(?:\"([^\"]*)\")?\s*$")
        self._code_end_pattern = re.compile(r"^```\s*$")

    def _can_handle(self, context: LineProcessingContext) -> bool:
        if self._is_inside_parent_context(context):
            return False
        return self._is_code_start(context)

    async def _process(self, context: LineProcessingContext) -> None:
        if self._is_code_start(context):
            await self._process_complete_code_block(context)

    def _is_code_start(self, context: LineProcessingContext) -> bool:
        """Check if this line starts a code block."""
        return self._code_start_pattern.match(context.line.strip()) is not None

    def _is_inside_parent_context(self, context: LineProcessingContext) -> bool:
        """Check if we're currently inside any parent context (toggle, heading, etc.)."""
        return len(context.parent_stack) > 0

    async def _process_complete_code_block(self, context: LineProcessingContext) -> None:
        """Process the entire code block in one go using CodeMapper."""
        code_lines, lines_to_consume = self._collect_code_lines(context)

        block = CodeMapper.create_from_markdown_block(opening_line=context.line, code_lines=code_lines)

        if block:
            context.lines_consumed = lines_to_consume
            context.result_blocks.append(block)

    def _collect_code_lines(self, context: LineProcessingContext) -> tuple[list[str], int]:
        """Collect lines until closing fence and return (lines, count_to_consume)."""
        lines = []
        for idx, ln in enumerate(context.get_remaining_lines()):
            if self._code_end_pattern.match(ln.strip()):
                return lines, idx + 1
            lines.append(ln)
        rem = context.get_remaining_lines()
        return rem, len(rem)
