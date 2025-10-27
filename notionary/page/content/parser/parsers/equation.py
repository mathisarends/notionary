from typing import override

from notionary.blocks.schemas import CreateEquationBlock, EquationData
from notionary.page.content.parser.parsers.base import (
    BlockParsingContext,
    LineParser,
)
from notionary.page.content.syntax.definition import SyntaxDefinitionRegistry


class EquationParser(LineParser):
    def __init__(self, syntax_registry: SyntaxDefinitionRegistry) -> None:
        super().__init__(syntax_registry)
        self._syntax = syntax_registry.get_equation_syntax()

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        if context.is_inside_parent_context():
            return False
        return self._is_equation_delimiter(context.line)

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        equation_content = self._collect_equation_content(context)
        lines_consumed = self._count_lines_consumed(context)

        block = self._create_equation_block(
            opening_line=context.line, equation_lines=equation_content
        )

        if block:
            context.lines_consumed = lines_consumed
            context.result_blocks.append(block)

    def _is_equation_delimiter(self, line: str) -> bool:
        return self._syntax.regex_pattern.match(line) is not None

    def _collect_equation_content(self, context: BlockParsingContext) -> list[str]:
        content_lines = []

        for line in context.get_remaining_lines():
            if self._is_equation_delimiter(line):
                break
            content_lines.append(line)

        return content_lines

    def _count_lines_consumed(self, context: BlockParsingContext) -> int:
        for line_index, line in enumerate(context.get_remaining_lines()):
            if self._is_equation_delimiter(line):
                return line_index + 1

        return len(context.get_remaining_lines())

    def _create_equation_block(
        self, opening_line: str, equation_lines: list[str]
    ) -> CreateEquationBlock | None:
        if opening_line.strip() != self._syntax.start_delimiter:
            return None

        if not equation_lines:
            return None

        expression = "\n".join(equation_lines).strip()

        if expression:
            return CreateEquationBlock(equation=EquationData(expression=expression))

        return None
