import re
from typing import override

from notionary.exceptions.block_parsing import InsufficientColumnsError, InvalidColumnRatioSumError
from notionary.page.content.parser.pre_processsing.handlers.port import PreProcessor
from notionary.page.content.syntax.service import SyntaxRegistry

RATIO_TOLERANCE = 0.0001


class ColumnSyntaxPreProcessor(PreProcessor):
    def __init__(self, syntax_registry: SyntaxRegistry | None = None) -> None:
        self._syntax_registry = syntax_registry or SyntaxRegistry()
        self._column_list_syntax = self._syntax_registry.get_column_list_syntax()
        self._column_syntax = self._syntax_registry.get_column_syntax()

    @override
    def process(self, markdown_text: str) -> str:
        if not self._has_columns_blocks(markdown_text):
            return markdown_text

        columns_blocks = self._extract_columns_blocks(markdown_text)

        for content in columns_blocks:
            column_matches = self._find_column_blocks(content)
            column_count = len(column_matches)
            self._validate_minimum_columns(column_count)
            ratios = self._extract_ratios(column_matches)
            self._validate_ratios(ratios, column_count)
        return markdown_text

    def _has_columns_blocks(self, markdown_text: str) -> bool:
        return self._column_list_syntax.start_delimiter in markdown_text

    def _extract_columns_blocks(self, markdown_text: str) -> list[str]:
        columns_blocks = []
        lines = markdown_text.split("\n")
        for index, line in enumerate(lines):
            if line.strip() == self._column_list_syntax.start_delimiter:
                content = self._extract_block_content(lines, index + 1)
                if content is not None:
                    columns_blocks.append(content)
        return columns_blocks

    def _extract_block_content(self, lines: list[str], start_index: int) -> str | None:
        depth = 1
        end_index = start_index
        block_start = self._column_list_syntax.start_delimiter.split()[0]
        while end_index < len(lines) and depth > 0:
            line = lines[end_index].strip()
            if line.startswith(f"{block_start} "):
                depth += 1
            elif line == self._column_list_syntax.end_delimiter:
                depth -= 1
            end_index += 1
        if depth == 0:
            return "\n".join(lines[start_index : end_index - 1])
        return None

    def _find_column_blocks(self, content: str) -> list[re.Match]:
        return list(self._column_syntax.regex_pattern.finditer(content))

    def _validate_minimum_columns(self, column_count: int) -> None:
        if column_count < 2:
            raise InsufficientColumnsError(column_count)

    def _extract_ratios(self, column_matches: list[re.Match]) -> list[float]:
        ratios = []
        for match in column_matches:
            ratio_str = match.group(1)
            if ratio_str and ratio_str != "1":
                ratios.append(float(ratio_str))
        return ratios

    def _validate_ratios(self, ratios: list[float], column_count: int) -> None:
        if not ratios or len(ratios) != column_count:
            return
        total = sum(ratios)
        if abs(total - 1.0) > RATIO_TOLERANCE:
            raise InvalidColumnRatioSumError(total, RATIO_TOLERANCE)
