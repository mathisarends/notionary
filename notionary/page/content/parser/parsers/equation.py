import re

from notionary.blocks.schemas import CreateEquationBlock, EquationData
from notionary.page.content.parser.parsers.base import (
    LineParser,
    LineProcessingContext,
)


class EquationParser(LineParser):
    EQUATION_DELIMITER = "$$"

    def __init__(self) -> None:
        super().__init__()
        delimiter_pattern = rf"^{re.escape(self.EQUATION_DELIMITER)}\s*$"
        self._equation_delimiter_pattern = re.compile(delimiter_pattern)

    def _can_handle(self, context: LineProcessingContext) -> bool:
        if context.is_inside_parent_context():
            return False
        return self._is_equation_delimiter(context.line)

    async def _process(self, context: LineProcessingContext) -> None:
        equation_content = self._collect_equation_content(context)
        lines_consumed = self._count_lines_consumed(context)

        block = self._create_equation_block(opening_line=context.line, equation_lines=equation_content)

        if block:
            context.lines_consumed = lines_consumed
            context.result_blocks.append(block)

    def _is_equation_delimiter(self, line: str) -> bool:
        return self._equation_delimiter_pattern.match(line.strip()) is not None

    def _collect_equation_content(self, context: LineProcessingContext) -> list[str]:
        content_lines = []

        for line in context.get_remaining_lines():
            if self._is_equation_delimiter(line):
                break
            content_lines.append(line)

        return content_lines

    def _count_lines_consumed(self, context: LineProcessingContext) -> int:
        for line_index, line in enumerate(context.get_remaining_lines()):
            if self._is_equation_delimiter(line):
                return line_index + 1

        return len(context.get_remaining_lines())

    def _create_equation_block(self, opening_line: str, equation_lines: list[str]) -> CreateEquationBlock | None:
        if opening_line.strip() != self.EQUATION_DELIMITER:
            return None

        if not equation_lines:
            return None

        raw_content = "\n".join(equation_lines)
        fixed_lines = self._fix_latex_line_breaks(raw_content.splitlines())
        expression = "\n".join(fixed_lines).strip()

        if expression:
            return CreateEquationBlock(equation=EquationData(expression=expression))

        return None

    def _fix_latex_line_breaks(self, lines: list[str]) -> list[str]:
        fixed_lines = []

        for line in lines:
            backslash_match = re.search(r"(\\+)$", line)
            if backslash_match:
                backslashes = backslash_match.group(1)
                has_odd_backslashes = len(backslashes) % 2 == 1
                if has_odd_backslashes:
                    line = line + "\\"

            fixed_lines.append(line)

        return fixed_lines
