import math
from typing import override

from notionary.page.content.parser.pre_processsing.handlers.port import PreProcessor
from notionary.page.content.syntax.definition import MarkdownGrammar, SyntaxDefinitionRegistry
from notionary.utils.decorators import time_execution_sync
from notionary.utils.mixins.logging import LoggingMixin


class IndentationNormalizer(PreProcessor, LoggingMixin):
    def __init__(
        self, syntax_registry: SyntaxDefinitionRegistry | None = None, markdown_grammar: MarkdownGrammar | None = None
    ) -> None:
        super().__init__()
        self._syntax_registry = syntax_registry or SyntaxDefinitionRegistry()
        self._markdown_grammar = markdown_grammar or MarkdownGrammar()

        self._spaces_per_nesting_level = self._markdown_grammar.spaces_per_nesting_level
        self._code_block_start_delimiter = self._syntax_registry.get_code_syntax().start_delimiter

    @override
    @time_execution_sync()
    def process(self, markdown_text: str) -> str:
        if self._is_empty(markdown_text):
            return ""

        normalized = self._normalize_to_markdown_indentation(markdown_text)

        if normalized != markdown_text:
            self.logger.warning(
                "Corrected non-standard indentation. Check the result for formatting errors and use consistent indentation in the source."
            )

        return normalized

    def _is_empty(self, text: str) -> bool:
        return not text

    def _normalize_to_markdown_indentation(self, markdown_text: str) -> str:
        lines = markdown_text.split("\n")
        processed_lines = []
        inside_code_block = False

        for line in lines:
            if self._is_code_fence(line):
                inside_code_block = not inside_code_block
                processed_lines.append(line)
            elif inside_code_block:
                processed_lines.append(line)
            else:
                processed_lines.append(self._normalize_to_standard_indentation(line))

        return "\n".join(processed_lines)

    def _is_code_fence(self, line: str) -> bool:
        return line.lstrip().startswith(self._code_block_start_delimiter)

    def _normalize_to_standard_indentation(self, line: str) -> str:
        if self._is_blank_line(line):
            return ""

        indentation_level = self._round_to_nearest_indentation_level(line)
        content = self._extract_content(line)

        return self._build_indented_line(indentation_level, content)

    def _is_blank_line(self, line: str) -> bool:
        return not line.strip()

    def _round_to_nearest_indentation_level(self, line: str) -> int:
        leading_spaces = self._count_leading_spaces(line)
        return math.ceil(leading_spaces / self._spaces_per_nesting_level)

    def _count_leading_spaces(self, line: str) -> int:
        return len(line) - len(line.lstrip())

    def _extract_content(self, line: str) -> str:
        return line.lstrip()

    def _build_indented_line(self, level: int, content: str) -> str:
        standard_indent = self._create_standard_indent(level)
        return standard_indent + content

    def _create_standard_indent(self, level: int) -> str:
        spaces = level * self._spaces_per_nesting_level
        return " " * spaces
