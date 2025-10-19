from typing import override

from notionary.page.content.parser.pre_processsing.handlers.port import PreProcessor
from notionary.utils.decorators import time_execution_sync


class WhitespacePreProcessor(PreProcessor):
    @override
    @time_execution_sync()
    def process(self, markdown_text: str) -> str:
        if not markdown_text:
            return ""

        lines = markdown_text.split("\n")
        processed_lines = []
        code_block_lines = []
        non_code_lines = []
        in_code_block = False

        for line in lines:
            if self._is_code_fence(line):
                if in_code_block:
                    # Format and add code block
                    processed_lines.extend(self._format_code_block(code_block_lines))
                    processed_lines.append("```")
                    code_block_lines = []
                    in_code_block = False
                else:
                    # Format accumulated non-code lines before starting code block
                    if non_code_lines:
                        processed_lines.extend(self._format_code_block(non_code_lines))
                        non_code_lines = []

                    language = self._extract_language(line)
                    processed_lines.append(f"```{language}")
                    in_code_block = True
            elif in_code_block:
                code_block_lines.append(line)
            else:
                non_code_lines.append(line)

        # Format remaining non-code lines at the end
        if non_code_lines:
            processed_lines.extend(self._format_code_block(non_code_lines))

        return "\n".join(processed_lines)

    def _is_code_fence(self, line: str) -> bool:
        return line.lstrip().startswith("```")

    def _extract_language(self, fence_line: str) -> str:
        return fence_line.lstrip().removeprefix("```").strip()

    def _format_code_block(self, lines: list[str]) -> list[str]:
        if not lines:
            return []

        non_empty_lines = [line for line in lines if line.strip()]
        if not non_empty_lines:
            return ["" for _ in lines]

        min_indent = min(self._count_leading_spaces(line) for line in non_empty_lines)

        if min_indent == 0:
            return lines

        return [self._remove_indent(line, min_indent) for line in lines]

    def _count_leading_spaces(self, line: str) -> int:
        return len(line) - len(line.lstrip())

    def _remove_indent(self, line: str, indent_size: int) -> str:
        if not line.strip():
            return ""
        return line[indent_size:]
