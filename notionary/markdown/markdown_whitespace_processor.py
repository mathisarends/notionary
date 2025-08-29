"""
Markdown whitespace processing utilities.

Handles normalization of markdown text while preserving code blocks and their indentation.
"""

from typing import List, Tuple


class MarkdownWhitespaceProcessor:
    """
    Processes markdown text to normalize whitespace while preserving code block formatting.

    This processor handles:
    - Removing leading whitespace from regular lines
    - Preserving code block structure and indentation
    - Normalizing code block markers
    """

    @staticmethod
    def process_markdown_whitespace(markdown_text: str) -> str:
        """Process markdown text to normalize whitespace while preserving code blocks."""
        lines = markdown_text.split("\n")
        if not lines:
            return ""

        return MarkdownWhitespaceProcessor._process_whitespace_lines(lines)

    @staticmethod
    def _process_whitespace_lines(lines: list[str]) -> str:
        """Process all lines and return the processed markdown."""
        processed_lines = []
        in_code_block = False
        current_code_block = []

        for line in lines:
            processed_lines, in_code_block, current_code_block = (
                MarkdownWhitespaceProcessor._process_single_line(
                    line, processed_lines, in_code_block, current_code_block
                )
            )

        return "\n".join(processed_lines)

    @staticmethod
    def _process_single_line(
        line: str,
        processed_lines: list[str],
        in_code_block: bool,
        current_code_block: list[str],
    ) -> Tuple[list[str], bool, list[str]]:
        """Process a single line and return updated state."""
        if MarkdownWhitespaceProcessor._is_code_block_marker(line):
            return MarkdownWhitespaceProcessor._handle_code_block_marker(
                line, processed_lines, in_code_block, current_code_block
            )
        if in_code_block:
            current_code_block.append(line)
            return processed_lines, in_code_block, current_code_block
        else:
            processed_lines.append(line.lstrip())
            return processed_lines, in_code_block, current_code_block

    @staticmethod
    def _handle_code_block_marker(
        line: str,
        processed_lines: list[str],
        in_code_block: bool,
        current_code_block: list[str],
    ) -> Tuple[list[str], bool, list[str]]:
        """Handle code block start/end markers."""
        if not in_code_block:
            return MarkdownWhitespaceProcessor._start_code_block(line, processed_lines)
        else:
            return MarkdownWhitespaceProcessor._end_code_block(
                processed_lines, current_code_block
            )

    @staticmethod
    def _start_code_block(
        line: str, processed_lines: list[str]
    ) -> Tuple[list[str], bool, list[str]]:
        """Start a new code block."""
        processed_lines.append(
            MarkdownWhitespaceProcessor._normalize_code_block_start(line)
        )
        return processed_lines, True, []

    @staticmethod
    def _end_code_block(
        processed_lines: list[str], current_code_block: list[str]
    ) -> Tuple[list[str], bool, list[str]]:
        """End the current code block."""
        processed_lines.extend(
            MarkdownWhitespaceProcessor._normalize_code_block_content(
                current_code_block
            )
        )
        processed_lines.append("```")
        return processed_lines, False, []

    @staticmethod
    def _is_code_block_marker(line: str) -> bool:
        """Check if line is a code block marker."""
        return line.lstrip().startswith("```")

    @staticmethod
    def _normalize_code_block_start(line: str) -> str:
        """Normalize code block opening marker."""
        language = line.lstrip().replace("```", "", 1).strip()
        return "```" + language

    @staticmethod
    def _normalize_code_block_content(code_lines: List[str]) -> List[str]:
        """Normalize code block indentation."""
        if not code_lines:
            return []

        # Find minimum indentation from non-empty lines
        non_empty_lines = [line for line in code_lines if line.strip()]
        if not non_empty_lines:
            return [""] * len(code_lines)

        min_indent = min(len(line) - len(line.lstrip()) for line in non_empty_lines)
        if min_indent == 0:
            return code_lines

        # Remove common indentation
        return ["" if not line.strip() else line[min_indent:] for line in code_lines]
