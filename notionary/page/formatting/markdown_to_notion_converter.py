import re
from typing import Dict, Any, List, Optional, Tuple

from notionary.blocks import ColumnElement, BlockRegistry, BlockRegistryBuilder
from notionary.page.formatting.spacer_rules import SpacerRule, SpacerRuleEngine


class MarkdownToNotionConverter:
    """Refactored converter mit expliziten Spacer-Regeln"""

    def __init__(self, block_registry: Optional[BlockRegistry] = None):
        """Initialize the converter with an optional custom block registry."""
        self._block_registry = (
            block_registry or BlockRegistryBuilder().create_full_registry()
        )

        # Spacer-Engine mit konfigurierbaren Regeln
        self._spacer_engine = SpacerRuleEngine()

        # Pattern für andere Verarbeitungsschritte
        self.TOGGLE_ELEMENT_TYPES = ["ToggleElement", "ToggleableHeadingElement"]
        self.PIPE_CONTENT_PATTERN = r"^\|\s?(.*)$"

        if self._block_registry.contains(ColumnElement):
            ColumnElement.set_converter_callback(self.convert)

    def convert(self, markdown_text: str) -> List[Dict[str, Any]]:
        """Convert markdown text to Notion API block format."""
        if not markdown_text:
            return []

        # Spacer-Verarbeitung mit expliziten Regeln
        processed_markdown = self._add_spacers_with_rules(markdown_text)

        # Rest der Pipeline bleibt gleich
        all_blocks_with_positions = self._collect_all_blocks_with_positions(
            processed_markdown
        )
        all_blocks_with_positions.sort(key=lambda x: x[0])
        blocks = [block for _, _, block in all_blocks_with_positions]

        return self._process_block_spacing(blocks)

    def _add_spacers_with_rules(self, markdown_text: str) -> str:
        """Fügt Spacer mit expliziten Regeln hinzu"""
        lines = markdown_text.split("\n")
        processed_lines = []

        # Initialer State
        state = {
            "in_code_block": False,
            "last_line_was_spacer": False,
            "last_non_empty_was_heading": False,
            "has_content_before": False,
            "processed_lines": processed_lines,
        }

        for line_number, line in enumerate(lines):
            result_lines, state = self._spacer_engine.process_line(
                line, line_number, state
            )
            processed_lines.extend(result_lines)
            state["processed_lines"] = processed_lines

        return "\n".join(processed_lines)

    def add_custom_spacer_rule(self, rule: SpacerRule, priority: int = -1):
        """Fügt eine benutzerdefinierte Spacer-Regel hinzu

        Args:
            rule: Die hinzuzufügende Regel
            priority: Position in der Regelliste (-1 = am Ende)
        """
        if priority == -1:
            self._spacer_engine.rules.append(rule)
        else:
            self._spacer_engine.rules.insert(priority, rule)

    def get_spacer_rules_info(self) -> List[Dict[str, str]]:
        """Gibt Informationen über alle aktiven Spacer-Regeln zurück"""
        return [
            {"name": rule.name, "description": rule.description}
            for rule in self._spacer_engine.rules
        ]

    # Alle anderen Methoden bleiben unverändert...
    def _collect_all_blocks_with_positions(
        self, markdown_text: str
    ) -> List[Tuple[int, int, Dict[str, Any]]]:
        """Collect all blocks with their positions in the text."""
        all_blocks = []

        # Process toggleable elements first (both Toggle and ToggleableHeading)
        toggleable_blocks = self._identify_toggleable_blocks(markdown_text)

        # Process other multiline elements
        multiline_blocks = self._identify_multiline_blocks(
            markdown_text, toggleable_blocks
        )

        # Process remaining text line by line
        processed_blocks = toggleable_blocks + multiline_blocks
        line_blocks = self._process_text_lines(markdown_text, processed_blocks)

        # Combine all blocks
        all_blocks.extend(toggleable_blocks)
        all_blocks.extend(multiline_blocks)
        all_blocks.extend(line_blocks)

        return all_blocks

    def _identify_toggleable_blocks(
        self, text: str
    ) -> List[Tuple[int, int, Dict[str, Any]]]:
        """Identify all toggleable blocks (Toggle and ToggleableHeading) in the text."""
        toggleable_blocks = []

        # Find all toggleable elements
        toggleable_elements = self._get_toggleable_elements()

        if not toggleable_elements:
            return []

        for element in toggleable_elements:
            matches = element.find_matches(text, self.convert, context_aware=True)
            if matches:
                toggleable_blocks.extend(matches)

        return toggleable_blocks

    def _get_toggleable_elements(self):
        """Return all toggleable elements from the registry."""
        toggleable_elements = []
        for element in self._block_registry.get_elements():
            if (
                element.is_multiline()
                and hasattr(element, "match_markdown")
                and element.__name__ in self.TOGGLE_ELEMENT_TYPES
            ):
                toggleable_elements.append(element)
        return toggleable_elements

    def _identify_multiline_blocks(
        self, text: str, exclude_blocks: List[Tuple[int, int, Dict[str, Any]]]
    ) -> List[Tuple[int, int, Dict[str, Any]]]:
        """Identify all multiline blocks (except toggleable blocks)."""
        # Get all multiline elements except toggleable ones
        multiline_elements = self._get_non_toggleable_multiline_elements()

        if not multiline_elements:
            return []

        # Create set of positions to exclude
        excluded_ranges = self._create_excluded_position_set(exclude_blocks)

        multiline_blocks = []
        for element in multiline_elements:
            matches = element.find_matches(text)

            if not matches:
                continue

            # Add blocks that don't overlap with excluded positions
            for start_pos, end_pos, block in matches:
                if self._overlaps_with_excluded_positions(
                    start_pos, end_pos, excluded_ranges
                ):
                    continue
                multiline_blocks.append((start_pos, end_pos, block))

        return multiline_blocks

    def _get_non_toggleable_multiline_elements(self):
        """Get multiline elements that are not toggleable elements."""
        return [
            element
            for element in self._block_registry.get_multiline_elements()
            if element.__name__ not in self.TOGGLE_ELEMENT_TYPES
        ]

    def _create_excluded_position_set(self, exclude_blocks):
        """Create a set of positions to exclude based on block ranges."""
        excluded_positions = set()
        for start_pos, end_pos, _ in exclude_blocks:
            excluded_positions.update(range(start_pos, end_pos + 1))
        return excluded_positions

    def _overlaps_with_excluded_positions(self, start_pos, end_pos, excluded_positions):
        """Check if a range overlaps with any excluded positions."""
        return any(pos in excluded_positions for pos in range(start_pos, end_pos + 1))

    def _process_text_lines(
        self, text: str, exclude_blocks: List[Tuple[int, int, Dict[str, Any]]]
    ) -> List[Tuple[int, int, Dict[str, Any]]]:
        """Process text line by line, excluding already processed ranges and handling pipe syntax lines."""
        if not text:
            return []

        # Create set of excluded positions
        excluded_positions = self._create_excluded_position_set(exclude_blocks)

        line_blocks = []
        lines = text.split("\n")

        current_pos = 0
        current_paragraph = []
        paragraph_start = 0
        in_todo_sequence = False

        for line in lines:
            line_length = len(line) + 1  # +1 for newline
            line_end = current_pos + line_length - 1

            # Skip excluded lines and pipe syntax lines (they're part of toggleable content)
            if self._overlaps_with_excluded_positions(
                current_pos, line_end, excluded_positions
            ) or self._is_pipe_syntax_line(line):
                current_pos += line_length
                continue

            processed = self._process_line(
                line,
                current_pos,
                line_end,
                line_blocks,
                current_paragraph,
                paragraph_start,
                in_todo_sequence,
            )

            current_pos = processed["current_pos"]
            current_paragraph = processed["current_paragraph"]
            paragraph_start = processed["paragraph_start"]
            in_todo_sequence = processed["in_todo_sequence"]

        # Process remaining paragraph
        self._process_paragraph(
            current_paragraph, paragraph_start, current_pos, line_blocks
        )

        return line_blocks

    def _is_pipe_syntax_line(self, line: str) -> bool:
        """Check if a line uses pipe syntax (for nested content)."""
        return bool(re.match(self.PIPE_CONTENT_PATTERN, line))

    def _process_line(
        self,
        line: str,
        current_pos: int,
        line_end: int,
        line_blocks: List[Tuple[int, int, Dict[str, Any]]],
        current_paragraph: List[str],
        paragraph_start: int,
        in_todo_sequence: bool,
    ) -> Dict[str, Any]:
        """Process a single line of text."""
        line_length = len(line) + 1  # +1 for newline

        # Check for spacer
        if self._is_spacer_line(line):
            line_blocks.append((current_pos, line_end, self._create_empty_paragraph()))
            return self._update_line_state(
                current_pos + line_length,
                current_paragraph,
                paragraph_start,
                in_todo_sequence,
            )

        # Handle todo items
        todo_block = self._extract_todo_item(line)
        if todo_block:
            return self._process_todo_line(
                todo_block,
                current_pos,
                line_end,
                line_blocks,
                current_paragraph,
                paragraph_start,
                in_todo_sequence,
                line_length,
            )

        if in_todo_sequence:
            in_todo_sequence = False

        # Handle empty lines
        if not line.strip():
            self._process_paragraph(
                current_paragraph, paragraph_start, current_pos, line_blocks
            )
            return self._update_line_state(
                current_pos + line_length, [], paragraph_start, False
            )

        # Handle special blocks
        special_block = self._extract_special_block(line)
        if special_block:
            self._process_paragraph(
                current_paragraph, paragraph_start, current_pos, line_blocks
            )
            line_blocks.append((current_pos, line_end, special_block))
            return self._update_line_state(
                current_pos + line_length, [], paragraph_start, False
            )

        # Handle as paragraph
        if not current_paragraph:
            paragraph_start = current_pos
        current_paragraph.append(line)

        return self._update_line_state(
            current_pos + line_length,
            current_paragraph,
            paragraph_start,
            in_todo_sequence,
        )

    def _is_spacer_line(self, line: str) -> bool:
        """Check if a line is a spacer marker."""
        return line.strip() == self._spacer_engine.SPACER_MARKER

    def _process_todo_line(
        self,
        todo_block: Dict[str, Any],
        current_pos: int,
        line_end: int,
        line_blocks: List[Tuple[int, int, Dict[str, Any]]],
        current_paragraph: List[str],
        paragraph_start: int,
        in_todo_sequence: bool,
        line_length: int,
    ) -> Dict[str, Any]:
        """Process a line that contains a todo item."""
        # Finish paragraph if needed
        if not in_todo_sequence and current_paragraph:
            self._process_paragraph(
                current_paragraph, paragraph_start, current_pos, line_blocks
            )

        line_blocks.append((current_pos, line_end, todo_block))

        return self._update_line_state(
            current_pos + line_length, [], paragraph_start, True
        )

    def _update_line_state(
        self,
        current_pos: int,
        current_paragraph: List[str],
        paragraph_start: int,
        in_todo_sequence: bool,
    ) -> Dict[str, Any]:
        """Update and return the state after processing a line."""
        return {
            "current_pos": current_pos,
            "current_paragraph": current_paragraph,
            "paragraph_start": paragraph_start,
            "in_todo_sequence": in_todo_sequence,
        }

    def _extract_todo_item(self, line: str) -> Optional[Dict[str, Any]]:
        """Extract a todo item from a line if possible."""
        todo_elements = [
            element
            for element in self._block_registry.get_elements()
            if not element.is_multiline() and element.__name__ == "TodoElement"
        ]

        for element in todo_elements:
            if element.match_markdown(line):
                return element.markdown_to_notion(line)
        return None

    def _extract_special_block(self, line: str) -> Optional[Dict[str, Any]]:
        """Extract a special block (not paragraph) from a line if possible."""
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

    def _process_paragraph(
        self,
        paragraph_lines: List[str],
        start_pos: int,
        end_pos: int,
        blocks: List[Tuple[int, int, Dict[str, Any]]],
    ) -> None:
        """Process a paragraph and add it to blocks if valid."""
        if not paragraph_lines:
            return

        paragraph_text = "\n".join(paragraph_lines)
        block = self._block_registry.markdown_to_notion(paragraph_text)

        if block:
            blocks.append((start_pos, end_pos, block))

    def _process_block_spacing(
        self, blocks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Add spacing between blocks where needed."""
        if not blocks:
            return blocks

        final_blocks = []

        for block_index, current_block in enumerate(blocks):
            final_blocks.append(current_block)

            # Only add spacing after multiline blocks
            if not self._is_multiline_block_type(current_block.get("type")):
                continue

            # Check if we need to add a spacer
            if self._needs_spacer_after_block(blocks, block_index):
                final_blocks.append(self._create_empty_paragraph())

        return final_blocks

    def _needs_spacer_after_block(
        self, blocks: List[Dict[str, Any]], block_index: int
    ) -> bool:
        """Determine if we need to add a spacer after the current block."""
        # Check if this is the last block (no need for spacer)
        if block_index + 1 >= len(blocks):
            return False

        # Check if next block is already a spacer
        next_block = blocks[block_index + 1]
        if self._is_empty_paragraph(next_block):
            return False

        # No spacer needed
        return True

    def _create_empty_paragraph(self):
        """Create an empty paragraph block."""
        return {"type": "paragraph", "paragraph": {"rich_text": []}}

    def _is_multiline_block_type(self, block_type: str) -> bool:
        """Check if a block type corresponds to a multiline element."""
        if not block_type:
            return False

        multiline_elements = self._block_registry.get_multiline_elements()

        for element in multiline_elements:
            element_name = element.__name__.lower()
            if block_type in element_name:
                return True

            if hasattr(element, "match_notion"):
                dummy_block = {"type": block_type}
                if element.match_notion(dummy_block):
                    return True

        return False

    def _is_empty_paragraph(self, block: Dict[str, Any]) -> bool:
        """Check if a block is an empty paragraph."""
        if block.get("type") != "paragraph":
            return False

        rich_text = block.get("paragraph", {}).get("rich_text", [])
        return not rich_text or len(rich_text) == 0
