from typing import override

from notionary.page.content.parser.pre_processsing.handlers.port import PreProcessor


class IndentationNormalizer(PreProcessor):
    MARKDOWN_STANDARD_INDENT_SIZE = 4

    @override
    def process(self, markdown_text: str) -> str:
        if self._is_empty(markdown_text):
            return ""

        return self._normalize_to_markdown_indentation(markdown_text)

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
        return line.lstrip().startswith("```")

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
        return round(leading_spaces / self.MARKDOWN_STANDARD_INDENT_SIZE)

    def _count_leading_spaces(self, line: str) -> int:
        return len(line) - len(line.lstrip())

    def _extract_content(self, line: str) -> str:
        return line.lstrip()

    def _build_indented_line(self, level: int, content: str) -> str:
        standard_indent = self._create_standard_indent(level)
        return standard_indent + content

    def _create_standard_indent(self, level: int) -> str:
        spaces = level * self.MARKDOWN_STANDARD_INDENT_SIZE
        return " " * spaces
