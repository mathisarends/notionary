class MarkdownWhitespaceProcessor:
    """Helper class for processing markdown whitespace."""

    def __init__(self):
        self.processed_lines = []
        self.in_code_block = False
        self.current_code_block = []

    def process_lines(self, lines: list[str]) -> str:
        """Process all lines and return the processed markdown."""
        self.processed_lines = []
        self.in_code_block = False
        self.current_code_block = []

        for line in lines:
            self._process_single_line(line)

        # Handle unclosed code block
        if self.in_code_block and self.current_code_block:
            self._finish_code_block()

        return "\n".join(self.processed_lines)

    def _process_single_line(self, line: str) -> None:
        """Process a single line of markdown."""
        if self._is_code_block_marker(line):
            self._handle_code_block_marker(line)
            return

        if self.in_code_block:
            self.current_code_block.append(line)
            return

        # Regular text - remove leading whitespace
        self.processed_lines.append(line.lstrip())

    def _handle_code_block_marker(self, line: str) -> None:
        """Handle code block start/end markers."""
        if not self.in_code_block:
            # Starting new code block
            self.in_code_block = True
            self.processed_lines.append(self._normalize_code_block_start(line))
            self.current_code_block = []
        else:
            # Ending code block
            self._finish_code_block()

    def _finish_code_block(self) -> None:
        """Finish processing current code block."""
        self.processed_lines.extend(
            self._normalize_code_block_content(self.current_code_block)
        )
        self.processed_lines.append("```")
        self.in_code_block = False

    def _is_code_block_marker(self, line: str) -> bool:
        """Check if line is a code block marker."""
        return line.lstrip().startswith("```")

    def _normalize_code_block_start(self, line: str) -> str:
        """Normalize code block opening marker."""
        language = line.lstrip().replace("```", "", 1).strip()
        return "```" + language

    def _normalize_code_block_content(self, code_lines: list[str]) -> list[str]:
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
