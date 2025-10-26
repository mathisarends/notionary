import re
from typing import override

from notionary.exceptions.block_parsing import (
    InsufficientColumnsError,
    InvalidColumnRatioSumError,
)
from notionary.page.content.parser.pre_processsing.handlers.port import PreProcessor
from notionary.page.content.syntax.definition import (
    MarkdownGrammar,
    SyntaxDefinitionRegistry,
)
from notionary.utils.decorators import time_execution_sync
from notionary.utils.mixins.logging import LoggingMixin


class ColumnSyntaxPreProcessor(PreProcessor, LoggingMixin):
    _RATIO_TOLERANCE = 0.0001
    _MINIMUM_COLUMNS = 2

    def __init__(
        self,
        syntax_registry: SyntaxDefinitionRegistry | None = None,
        markdown_grammar: MarkdownGrammar | None = None,
    ) -> None:
        super().__init__()
        self._syntax_registry = syntax_registry or SyntaxDefinitionRegistry()
        self._markdown_grammar = markdown_grammar or MarkdownGrammar()

        self._spaces_per_nesting_level = self._markdown_grammar.spaces_per_nesting_level
        self._column_list_delimiter = (
            self._syntax_registry.get_column_list_syntax().start_delimiter
        )
        self._column_delimiter = (
            self._syntax_registry.get_column_syntax().start_delimiter
        )
        self._column_pattern = self._syntax_registry.get_column_syntax().regex_pattern

    @override
    @time_execution_sync()
    def process(self, markdown_text: str) -> str:
        if not self._contains_column_lists(markdown_text):
            return markdown_text

        self._validate_all_column_lists(markdown_text)
        return markdown_text

    def _contains_column_lists(self, markdown_text: str) -> bool:
        return self._column_list_delimiter in markdown_text

    def _validate_all_column_lists(self, markdown_text: str) -> None:
        column_list_blocks = self._extract_column_list_blocks(markdown_text)

        for block in column_list_blocks:
            self._validate_column_list_block(block)

    def _extract_column_list_blocks(self, markdown_text: str) -> list[str]:
        lines = markdown_text.split("\n")
        blocks = []

        for index, line in enumerate(lines):
            if self._is_column_list_start(line):
                block_content = self._extract_indented_block(lines, index + 1)
                blocks.append(block_content)

        return blocks

    def _is_column_list_start(self, line: str) -> bool:
        return line.strip() == self._column_list_delimiter

    def _extract_indented_block(self, lines: list[str], start_index: int) -> str:
        if start_index >= len(lines):
            return ""

        base_indentation = self._get_indentation_level(lines[start_index])
        base_spaces = base_indentation * self._spaces_per_nesting_level
        block_lines = []

        for line in lines[start_index:]:
            if self._is_empty_line(line):
                block_lines.append(line)
                continue

            current_indentation = self._get_indentation_level(line)

            if current_indentation < base_indentation:
                break

            block_lines.append(line[base_spaces:] if len(line) >= base_spaces else line)

        return "\n".join(block_lines)

    def _is_empty_line(self, line: str) -> bool:
        return not line.strip()

    def _get_indentation_level(self, line: str) -> int:
        leading_spaces = len(line) - len(line.lstrip())
        return leading_spaces // self._spaces_per_nesting_level

    def _validate_column_list_block(self, block_content: str) -> None:
        column_matches = self._find_all_columns(block_content)
        column_count = len(column_matches)

        self._validate_minimum_column_count(column_count)

        ratios = self._extract_column_ratios(column_matches)
        self._validate_ratio_sum(ratios, column_count)

    def _find_all_columns(self, content: str) -> list[re.Match]:
        return list(self._column_pattern.finditer(content))

    def _validate_minimum_column_count(self, column_count: int) -> None:
        if column_count < self._MINIMUM_COLUMNS:
            self.logger.error(
                f"Column list must contain at least {self._MINIMUM_COLUMNS} columns, found {column_count}"
            )
            raise InsufficientColumnsError(column_count)

    def _extract_column_ratios(self, column_matches: list[re.Match]) -> list[float]:
        ratios = []

        for match in column_matches:
            ratio_text = match.group(1)
            if self._has_explicit_ratio(ratio_text):
                ratios.append(float(ratio_text))

        return ratios

    def _has_explicit_ratio(self, ratio_text: str | None) -> bool:
        return ratio_text is not None and ratio_text != "1"

    def _validate_ratio_sum(self, ratios: list[float], column_count: int) -> None:
        if not self._should_validate_ratios(ratios, column_count):
            return

        total_ratio = sum(ratios)

        if not self._is_ratio_sum_valid(total_ratio):
            self.logger.error(
                f"Column ratios must sum to 1.0 (±{self._RATIO_TOLERANCE}), but sum to {total_ratio:.4f}"
            )
            raise InvalidColumnRatioSumError(total_ratio, self._RATIO_TOLERANCE)

    def _should_validate_ratios(self, ratios: list[float], column_count: int) -> bool:
        return len(ratios) > 0 and len(ratios) == column_count

    def _is_ratio_sum_valid(self, total: float) -> bool:
        return abs(total - 1.0) <= self._RATIO_TOLERANCE
