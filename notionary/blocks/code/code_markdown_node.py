from notionary.blocks.markdown.markdown_node import MarkdownNode


class CodeMarkdownNode(MarkdownNode):
    """
    Enhanced Code node with Pydantic integration.
    Programmatic interface for creating Notion-style Markdown code blocks.
    Automatically handles indentation normalization for multiline strings.

    Example:
        ```python "Basic usage"
        print("Hello, world!")
        ```
    """

    code: str
    language: str | None = None
    caption: str | None = None

    def to_markdown(self) -> str:
        lang = self.language or ""

        # Build the opening fence with optional caption
        opening_fence = f"```{lang}"
        if self.caption:
            opening_fence += f' "{self.caption}"'

        # Smart indentation normalization
        normalized_code = self._normalize_indentation(self.code)

        content = f"{opening_fence}\n{normalized_code}\n```"
        return content

    def _normalize_indentation(self, code: str) -> str:
        """Normalize indentation by removing common leading whitespace."""
        lines = code.strip().split("\n")

        if self._is_empty_or_single_line(lines):
            return self._handle_simple_cases(lines)

        min_indentation = self._find_minimum_indentation_excluding_first_line(lines)
        return self._remove_common_indentation(lines, min_indentation)

    def _is_empty_or_single_line(self, lines: list[str]) -> bool:
        return not lines or len(lines) == 1

    def _handle_simple_cases(self, lines: list[str]) -> str:
        if not lines:
            return ""
        return lines[0].strip()

    def _find_minimum_indentation_excluding_first_line(self, lines: list[str]) -> int:
        non_empty_lines_after_first = [line for line in lines[1:] if line.strip()]

        if not non_empty_lines_after_first:
            return 0

        return min(len(line) - len(line.lstrip()) for line in non_empty_lines_after_first)

    def _remove_common_indentation(self, lines: list[str], min_indentation: int) -> str:
        normalized_lines = [lines[0].strip()]

        for line in lines[1:]:
            normalized_line = self._normalize_single_line(line, min_indentation)
            normalized_lines.append(normalized_line)

        return "\n".join(normalized_lines)

    def _normalize_single_line(self, line: str, min_indentation: int) -> str:
        if not line.strip():
            return ""

        if len(line) > min_indentation:
            return line[min_indentation:]

        return line.strip()
