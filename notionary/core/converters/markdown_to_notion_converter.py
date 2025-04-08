from typing import Dict, Any, List, Optional, Tuple

from notionary.core.converters.registry.block_element_registry import BlockElementRegistry
from notionary.core.converters.registry.block_element_registry_builder import BlockElementRegistryBuilder

class MarkdownToNotionConverter:
    SPACER_MARKER = "<!-- spacer -->"
    MULTILINE_CONTENT_MARKER = "<!-- REMOVED_MULTILINE_CONTENT -->"
    TOGGLE_MARKER = "<!-- toggle_content -->"
    
    def __init__(self, block_registry: Optional[BlockElementRegistry] = None):
        """
        Initialize the MarkdownToNotionConverter.

        Args:
            block_registry: Optional registry of Notion block elements
        """
        self.block_registry = block_registry or BlockElementRegistryBuilder().create_standard_registry()
        

    def convert(self, markdown_text: str) -> List[Dict[str, Any]]:
        """
        Convert markdown text to Notion API block format.

        Args:
            markdown_text: The markdown text to convert

        Returns:
            List of Notion blocks
        """
        if not markdown_text:
            return []

        # Process toggles first
        processed_text, toggle_blocks = self._extract_toggle_elements(markdown_text)

        # Process other multiline elements
        processed_text, multiline_blocks = self._extract_multiline_elements(processed_text)

        # Process remaining text line by line
        line_blocks = self._process_text_lines(processed_text)

        # Combine and sort all blocks
        all_blocks = toggle_blocks + multiline_blocks + line_blocks
        all_blocks.sort(key=lambda x: x[0])

        # Extract just the blocks from position tuples
        blocks = [block for _, _, block in all_blocks]

        # Process spacing between blocks
        return self._process_block_spacing(blocks)

    def _extract_toggle_elements(
        self, text: str
    ) -> Tuple[str, List[Tuple[int, int, Dict[str, Any]]]]:
        """
        Extract toggle elements and their nested content.

        Args:
            text: The text to process

        Returns:
            Tuple of (processed text, list of (start_pos, end_pos, block) tuples)
        """
        from notionary.core.converters import default_registry # type: ignore
        
        toggle_blocks = []
        lines = text.split("\n")
        processed_lines = []

        i = 0
        while i < len(lines):
            line = lines[i]

            toggle_element = self._find_toggle_element(line, default_registry)
            
            if not toggle_element:
                processed_lines.append(line)
                i += 1
                continue
                
            # Toggle element found - process it
            toggle_start_pos = len("\n".join(processed_lines)) + (
                len(processed_lines) if processed_lines else 0
            )
            toggle_block = toggle_element.markdown_to_notion(line)

            # Extract nested content
            nested_content, j = self._extract_toggle_nested_content(lines, i + 1)
            
            # Process nested content recursively
            if nested_content:
                nested_text = "\n".join(nested_content)
                nested_blocks = self.convert(nested_text)
                if nested_blocks:
                    toggle_block["toggle"]["children"] = nested_blocks

            # Calculate toggle end position
            toggle_end_pos = (
                toggle_start_pos
                + len(line)
                + sum([len(l) + 1 for l in nested_content])
            )

            # Add the toggle block to our list
            toggle_blocks.append((toggle_start_pos, toggle_end_pos, toggle_block))

            # Add placeholders for the toggle and its content
            processed_lines.append(self.TOGGLE_MARKER)
            toggle_content_lines = [self.TOGGLE_MARKER] * len(nested_content)
            processed_lines.extend(toggle_content_lines)

            # Skip to after the toggle content
            i = j

        processed_text = "\n".join(processed_lines)
        return processed_text, toggle_blocks
        
    def _find_toggle_element(self, line: str, registry):
        """Find matching toggle element for a line if one exists."""
        for element in registry.get_elements():
            if (
                element.is_multiline()
                and hasattr(element, "match_markdown")
                and element.__name__ == "ToggleElement"
                and element.match_markdown(line)
            ):
                return element
        return None
        
    def _extract_toggle_nested_content(self, lines: List[str], start_index: int) -> Tuple[List[str], int]:
        """
        Extract the nested content of a toggle element.
        
        Args:
            lines: All lines of text
            start_index: Starting index to look for nested content
            
        Returns:
            Tuple of (nested_content_lines, next_line_index)
        """
        nested_content = []
        j = start_index

        # This is the pattern for indented content - 2 or more spaces or tabs
        while j < len(lines):
            next_line = lines[j]

            # Empty line still part of toggle content
            if not next_line.strip():
                nested_content.append("")
                j += 1
                continue

            # Indented content belongs to toggle
            if next_line.startswith("  ") or next_line.startswith("\t"):
                # Remove indentation (either tabs or 2+ spaces)
                if next_line.startswith("\t"):
                    content_line = next_line[1:]
                else:
                    # Find number of leading spaces
                    leading_spaces = len(next_line) - len(next_line.lstrip(" "))
                    # Remove at least 2 spaces
                    content_line = next_line[min(2, leading_spaces):]

                nested_content.append(content_line)
                j += 1
                continue

            # Non-indented, non-empty line marks the end of toggle content
            break

        return nested_content, j

    def _extract_multiline_elements(
        self, text: str
    ) -> Tuple[str, List[Tuple[int, int, Dict[str, Any]]]]:
        """
        Extract multiline elements and remove them from the text.

        Args:
            text: The text to process

        Returns:
            Tuple of (processed text, list of (start_pos, end_pos, block) tuples)
        """
        from notionary.core.converters import default_registry # type: ignore
        
        if not text:
            return text, []
            
        multiline_blocks = []
        processed_text = text

        # Get all multiline elements except ToggleElement
        multiline_elements = [
            element for element in default_registry.get_multiline_elements()
            if element.__name__ != "ToggleElement"
        ]
        
        if not multiline_elements:
            return text, []

        for element in multiline_elements:
            if not hasattr(element, "find_matches"):
                continue
                
            # Find all matches for this element
            matches = element.find_matches(processed_text)
            if not matches:
                continue
                
            multiline_blocks.extend(matches)

            # Remove matched content from the text to avoid processing it again
            processed_text = self._replace_matched_content_with_markers(processed_text, matches)

        return processed_text, multiline_blocks
        
    def _replace_matched_content_with_markers(self, text: str, matches: List[Tuple[int, int, Dict[str, Any]]]) -> str:
        """Replace matched content with marker placeholders to preserve line structure."""
        for start, end, _ in reversed(matches):
            num_newlines = text[start:end].count("\n")
            # Use a marker that won't be processed as markdown
            text = (
                text[:start]
                + "\n"
                + self.MULTILINE_CONTENT_MARKER
                + "\n" * num_newlines
                + text[end:]
            )
        return text

    def _process_text_lines(self, text: str) -> List[Tuple[int, int, Dict[str, Any]]]:
        """
        Process text line by line for single-line elements.

        Args:
            text: The text to process

        Returns:
            List of (start_pos, end_pos, block) tuples
        """
        if not text:
            return []

        line_blocks = []
        lines = text.split("\n")

        current_pos = 0
        current_paragraph = []
        paragraph_start = 0
        in_todo_sequence = False

        for line in lines:
            line_length = len(line) + 1  # +1 for newline

            # Skip marker lines
            if self._is_marker_line(line):
                current_pos += line_length
                continue

            # Check for spacer marker
            if self._is_spacer_marker(line):
                line_blocks.append(
                    (
                        current_pos,
                        current_pos + line_length,
                        self._create_empty_paragraph(),
                    )
                )
                current_pos += line_length
                continue

            # Process todos first to keep them grouped
            todo_block = self._extract_todo_item(line)
            if todo_block:
                self._handle_todo_item(
                    todo_block,
                    line_length,
                    current_pos,
                    current_paragraph,
                    paragraph_start,
                    line_blocks,
                    in_todo_sequence,
                )
                in_todo_sequence = True
                current_pos += line_length
                continue

            # No longer in a todo sequence
            if in_todo_sequence:
                in_todo_sequence = False

            # Handle empty lines
            if not line.strip():
                self._process_paragraph_if_present(
                    current_paragraph, paragraph_start, current_pos, line_blocks
                )
                current_paragraph = []
                current_pos += line_length
                continue

            # Check for other special blocks
            special_block = self._extract_special_block(line)
            if special_block:
                self._process_paragraph_if_present(
                    current_paragraph, paragraph_start, current_pos, line_blocks
                )
                line_blocks.append((current_pos, current_pos + line_length, special_block))
                current_paragraph = []
                current_pos += line_length
                continue

            # Handle as part of paragraph
            if not current_paragraph:
                paragraph_start = current_pos
            current_paragraph.append(line)
            current_pos += line_length

        # Process any remaining paragraph content
        self._process_paragraph_if_present(
            current_paragraph, paragraph_start, current_pos, line_blocks
        )

        return line_blocks
        
    def _is_marker_line(self, line: str) -> bool:
        """Check if a line is any kind of marker line that should be skipped."""
        return self._is_multiline_marker(line) or self._is_toggle_marker(line)

    def _is_multiline_marker(self, line: str) -> bool:
        """Check if a line is a multiline content marker."""
        return line.strip() == self.MULTILINE_CONTENT_MARKER

    def _is_toggle_marker(self, line: str) -> bool:
        """Check if a line is a toggle content marker."""
        return line.strip() == self.TOGGLE_MARKER

    def _is_spacer_marker(self, line: str) -> bool:
        """Check if a line is a spacer marker."""
        return line.strip() == self.SPACER_MARKER

    def _extract_todo_item(self, line: str) -> Optional[Dict[str, Any]]:
        """
        Try to extract a todo item from a line.

        Returns:
            Todo block if line is a todo item, None otherwise
        """
        from notionary.core.converters import default_registry # type: ignore
        
        for element in default_registry.get_elements():
            if (
                not element.is_multiline()
                and hasattr(element, "match_markdown")
                and element.__name__ == "TodoElement"
                and element.match_markdown(line)
            ):
                return element.markdown_to_notion(line)
        return None

    def _handle_todo_item(
        self,
        todo_block: Dict[str, Any],
        line_length: int,
        current_pos: int,
        current_paragraph: List[str],
        paragraph_start: int,
        line_blocks: List[Tuple[int, int, Dict[str, Any]]],
        in_todo_sequence: bool,
    ) -> None:
        """Handle a todo item line."""
        # If we were building a paragraph, finish it before starting todos
        if not in_todo_sequence and current_paragraph:
            self._process_paragraph_if_present(
                current_paragraph, paragraph_start, current_pos, line_blocks
            )
            current_paragraph.clear()

        line_blocks.append((current_pos, current_pos + line_length, todo_block))

    def _extract_special_block(self, line: str) -> Optional[Dict[str, Any]]:
        """
        Try to extract a special block (not paragraph) from a line.

        Returns:
            Block if line is a special block, None otherwise
        """
        from notionary.core.converters import default_registry # type: ignore     
        
        for element in default_registry.get_elements():
            if (
                not element.is_multiline()
                and hasattr(element, "match_markdown")
                and element.match_markdown(line)
            ):
                block = element.markdown_to_notion(line)
                if block and block.get("type") != "paragraph":
                    return block
        return None

    def _process_paragraph_if_present(
        self,
        paragraph_lines: List[str],
        start_pos: int,
        end_pos: int,
        blocks: List[Tuple[int, int, Dict[str, Any]]],
    ) -> None:
        """
        Process a paragraph and add it to the blocks list if valid.

        Args:
            paragraph_lines: Lines that make up the paragraph
            start_pos: Starting position of the paragraph
            end_pos: Ending position of the paragraph
            blocks: List to add the processed paragraph block to
        """
        if not paragraph_lines:
            return

        from notionary.core.converters import default_registry # type: ignore
        
        paragraph_text = "\n".join(paragraph_lines)
        block = default_registry.markdown_to_notion(paragraph_text)

        if not block:
            return

        blocks.append((start_pos, end_pos, block))

    def _process_block_spacing(
        self, blocks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Process blocks and add spacing only where no explicit spacer is present.

        Args:
            blocks: List of Notion blocks

        Returns:
            List of Notion blocks with processed spacing
        """
        if not blocks:
            return blocks

        final_blocks = []
        i = 0

        while i < len(blocks):
            current_block = blocks[i]
            final_blocks.append(current_block)

            # Check if this is a multiline element that needs spacing
            if not self._is_multiline_block_type(current_block.get("type")):
                i += 1
                continue
                
            # Check if the next block is already a spacer
            if i + 1 < len(blocks) and self._is_empty_paragraph(blocks[i + 1]):
                # Next block is already a spacer, don't add another
                pass
            else:
                # No explicit spacer found, add one automatically
                final_blocks.append(self._create_empty_paragraph())

            i += 1

        return final_blocks

    def _is_multiline_block_type(self, block_type: str) -> bool:
        """
        Check if a block type corresponds to a multiline element.

        Args:
            block_type: The type of block to check

        Returns:
            True if the block type is a multiline element, False otherwise
        """
        if not block_type:
            return False

        from notionary.core.converters import default_registry # type: ignore
        
        multiline_elements = default_registry.get_multiline_elements()

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
        """
        Check if a block is an empty paragraph.

        Args:
            block: The block to check

        Returns:
            True if it's an empty paragraph, False otherwise
        """
        if block.get("type") != "paragraph":
            return False
            
        rich_text = block.get("paragraph", {}).get("rich_text", [])
        return not rich_text or len(rich_text) == 0

    def _create_empty_paragraph(self) -> Dict[str, Any]:
        """
        Create an empty paragraph block.

        Returns:
            Empty paragraph block dictionary
        """
        return {"type": "paragraph", "paragraph": {"rich_text": []}}