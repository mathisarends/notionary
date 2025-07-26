import re
from typing import Optional
from notionary.blocks.registry.block_registry import BlockRegistry


class LineProcessingState:
    """Tracks state during line-by-line processing"""

    def __init__(self):
        self.paragraph_lines: list[str] = []
        self.paragraph_start: int = 0
        self.in_todo_sequence: bool = False

    def add_to_paragraph(self, line: str, current_pos: int):
        """Add line to current paragraph"""
        if not self.paragraph_lines:
            self.paragraph_start = current_pos
        self.paragraph_lines.append(line)

    def reset_paragraph(self):
        """Reset paragraph state"""
        self.paragraph_lines = []
        self.paragraph_start = 0

    def has_paragraph(self) -> bool:
        """Check if there are paragraph lines to process"""
        return len(self.paragraph_lines) > 0


class LineProcessor:
    """Handles line-by-line processing of markdown text"""

    def __init__(
        self,
        block_registry: BlockRegistry,
        excluded_ranges: set[int],
        pipe_pattern: str,
    ):
        self._block_registry = block_registry
        self._excluded_ranges = excluded_ranges
        self._pipe_pattern = pipe_pattern

    def process_lines(self, text: str) -> list[tuple[int, int, dict[str, any]]]:
        """Process all lines and return blocks with positions"""
        lines = text.split("\n")
        line_blocks = []

        state = LineProcessingState()
        current_pos = 0

        for line in lines:
            line_length = len(line) + 1  # +1 for newline
            line_end = current_pos + line_length - 1

            if self._should_skip_line(line, current_pos, line_end):
                current_pos += line_length
                continue

            self._process_single_line(line, current_pos, line_end, line_blocks, state)
            current_pos += line_length

        # Process any remaining paragraph
        self._finalize_paragraph(state, current_pos, line_blocks)

        return line_blocks

    def _should_skip_line(self, line: str, current_pos: int, line_end: int) -> bool:
        """Check if line should be skipped (excluded or pipe syntax)"""
        return self._overlaps_with_excluded(
            current_pos, line_end
        ) or self._is_pipe_syntax_line(line)

    def _overlaps_with_excluded(self, start_pos: int, end_pos: int) -> bool:
        """Check if position range overlaps with excluded ranges"""
        return any(
            pos in self._excluded_ranges for pos in range(start_pos, end_pos + 1)
        )

    def _is_pipe_syntax_line(self, line: str) -> bool:
        """Check if line uses pipe syntax for nested content"""
        return bool(re.match(self._pipe_pattern, line))

    def _process_single_line(
        self,
        line: str,
        current_pos: int,
        line_end: int,
        line_blocks: list[tuple[int, int, dict[str, any]]],
        state: LineProcessingState,
    ):
        """Process a single line of text"""
        # Handle todo items
        todo_block = self._extract_todo_item(line)
        if todo_block:
            self._handle_todo_line(
                todo_block, current_pos, line_end, line_blocks, state
            )
            return

        # Reset todo sequence if we were in one
        state.in_todo_sequence = False

        # Handle empty lines
        if not line.strip():
            self._finalize_paragraph(state, current_pos, line_blocks)
            state.reset_paragraph()
            return

        # Handle special blocks (headings, etc.)
        special_block = self._extract_special_block(line)
        if special_block:
            self._finalize_paragraph(state, current_pos, line_blocks)
            line_blocks.append((current_pos, line_end, special_block))
            state.reset_paragraph()
            return

        # Add to current paragraph
        state.add_to_paragraph(line, current_pos)

    def _extract_todo_item(self, line: str) -> Optional[dict[str, any]]:
        """Extract todo item from line if present"""
        todo_elements = [
            element
            for element in self._block_registry.get_elements()
            if not element.is_multiline() and element.__name__ == "TodoElement"
        ]

        for element in todo_elements:
            if element.match_markdown(line):
                return element.markdown_to_notion(line)
        return None

    def _extract_special_block(self, line: str) -> Optional[dict[str, any]]:
        """Extract special block (non-paragraph) from line"""
        non_multiline_elements = [
            element
            for element in self._block_registry.get_elements()
            if not element.is_multiline()
        ]

        for element in non_multiline_elements:
            if element.match_markdown(line):
                block = element.markdown_to_notion(line)
                if block and block.get("type") != "paragraph":
                    return block
        return None

    def _handle_todo_line(
        self,
        todo_block: dict[str, any],
        current_pos: int,
        line_end: int,
        line_blocks: list[tuple[int, int, dict[str, any]]],
        state: LineProcessingState,
    ):
        """Handle a line containing a todo item"""
        # Finish current paragraph if starting new todo sequence
        if not state.in_todo_sequence and state.has_paragraph():
            self._finalize_paragraph(state, current_pos, line_blocks)

        line_blocks.append((current_pos, line_end, todo_block))
        state.reset_paragraph()
        state.in_todo_sequence = True

    def _finalize_paragraph(
        self,
        state: LineProcessingState,
        end_pos: int,
        line_blocks: list[tuple[int, int, dict[str, any]]],
    ):
        """Convert current paragraph lines to paragraph block"""
        if not state.has_paragraph():
            return

        paragraph_text = "\n".join(state.paragraph_lines)
        block = self._block_registry.markdown_to_notion(paragraph_text)

        if block:
            line_blocks.append((state.paragraph_start, end_pos, block))
