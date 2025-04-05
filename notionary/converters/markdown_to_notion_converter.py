from typing import Dict, Any, List, Optional, Tuple
from notionary.converters.notion_element_registry import ElementRegistry

class MarkdownToNotionConverter:
    SPACER_MARKER = '<!-- spacer -->'
    MULTILINE_CONTENT_MARKER = '<!-- REMOVED_MULTILINE_CONTENT -->'
    TOGGLE_MARKER = '<!-- toggle_content -->'
    
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
        processed_text, toggle_blocks = self._process_toggle_elements(markdown_text)
        
        # Process other multiline elements
        processed_text, multiline_blocks = self._process_multiline_elements(processed_text)
        
        line_blocks = self._process_text_lines(processed_text)
        
        all_blocks = toggle_blocks + multiline_blocks + line_blocks
        all_blocks.sort(key=lambda x: x[0])
        
        blocks = [block for _, _, block in all_blocks]
        
        final_blocks = self._process_explicit_spacing(blocks)
        
        return final_blocks
    
    def _process_toggle_elements(self, text: str) -> Tuple[str, List[Tuple[int, int, Dict[str, Any]]]]:
        """
        Process toggle elements and their nested content.
        
        Args:
            text: The text to process
            
        Returns:
            Tuple of (processed text, list of (start_pos, end_pos, block) tuples)
        """
        toggle_blocks = []
        lines = text.split('\n')
        processed_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check if the line is a toggle
            toggle_element = None
            for element in ElementRegistry.get_elements():
                if (element.is_multiline() and 
                    hasattr(element, 'match_markdown') and 
                    element.__name__ == 'ToggleElement' and
                    element.match_markdown(line)):
                    toggle_element = element
                    break
            
            if toggle_element:
                toggle_start_pos = len('\n'.join(processed_lines)) + (len(processed_lines) if processed_lines else 0)
                toggle_block = toggle_element.markdown_to_notion(line)
                
                # Collect indented content for the toggle
                nested_content = []
                j = i + 1
                
                # This is the pattern for indented content - 2 or more spaces or tabs
                indent_pattern = lambda l: l.startswith('  ') or l.startswith('\t')
                
                while j < len(lines):
                    next_line = lines[j]
                    
                    # Empty line still part of toggle content
                    if not next_line.strip():
                        nested_content.append("")
                        j += 1
                        continue
                    
                    # Indented content belongs to toggle
                    if indent_pattern(next_line):
                        # Remove indentation (either tabs or 2+ spaces)
                        if next_line.startswith('\t'):
                            content_line = next_line[1:]
                        else:
                            # Find number of leading spaces
                            leading_spaces = len(next_line) - len(next_line.lstrip(' '))
                            # Remove at least 2 spaces
                            content_line = next_line[min(2, leading_spaces):]
                        
                        nested_content.append(content_line)
                        j += 1
                        continue
                    
                    # Non-indented, non-empty line marks the end of toggle content
                    break
                
                # Process nested content recursively
                if nested_content:
                    nested_text = '\n'.join(nested_content)
                    nested_blocks = self.convert(nested_text)
                    if nested_blocks:
                        toggle_block["toggle"]["children"] = nested_blocks
                
                # Calculate toggle end position
                toggle_end_pos = toggle_start_pos + len(line) + sum([len(l) + 1 for l in nested_content])
                
                # Add the toggle block to our list
                toggle_blocks.append((toggle_start_pos, toggle_end_pos, toggle_block))
                
                # Add a placeholder for the toggle and its content
                # IMPORTANT: Don't add the original toggle line to processed_lines, 
                # instead add a marker to completely remove it from output
                processed_lines.append(self.TOGGLE_MARKER)
                toggle_content_lines = [self.TOGGLE_MARKER] * len(nested_content)
                processed_lines.extend(toggle_content_lines)
                
                # Skip to after the toggle content
                i = j
            else:
                processed_lines.append(line)
                i += 1
        
        processed_text = '\n'.join(processed_lines)
        return processed_text, toggle_blocks
    
    def _process_multiline_elements(self, text: str) -> Tuple[str, List[Tuple[int, int, Dict[str, Any]]]]:
        """
        Process multiline elements and remove them from the text.
        
        Args:
            text: The text to process
            
        Returns:
            Tuple of (processed text, list of (start_pos, end_pos, block) tuples)
        """
        multiline_blocks = []
        processed_text = text
        
        # Get all multiline elements
        multiline_elements = ElementRegistry.get_multiline_elements()
        
        for element in multiline_elements:
            # Skip ToggleElement as it's handled separately
            if element.__name__ == 'ToggleElement':
                continue
                
            if hasattr(element, 'find_matches'):
                # Find all matches for this element
                matches = element.find_matches(processed_text)
                if matches:
                    multiline_blocks.extend(matches)
                    
                    # Remove matched content from the text to avoid processing it again
                    # Use a special marker instead of just newlines to preserve line structure
                    for start, end, _ in reversed(matches):
                        num_newlines = processed_text[start:end].count('\n')
                        # Use a marker that won't be processed as markdown
                        processed_text = processed_text[:start] + '\n' + self.MULTILINE_CONTENT_MARKER + '\n' * num_newlines + processed_text[end:]
        
        return processed_text, multiline_blocks
    
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
        lines = text.split('\n')
        
        current_pos = 0
        current_paragraph = []
        paragraph_start = 0
        in_todo_sequence = False
        
        for line in lines:
            line_length = len(line) + 1  # +1 for newline
            
            # Skip marker lines
            if self._is_multiline_marker(line) or self._is_toggle_marker(line):
                current_pos += line_length
                continue
            
            # Überprüfe auf Spacer-Marker
            if self._is_spacer_marker(line):
                line_blocks.append((current_pos, current_pos + line_length, self._create_empty_paragraph()))
                current_pos += line_length
                continue
            
            # Process todos first to keep them grouped
            todo_block = self._try_process_todo_item(line)
            if todo_block:
                self._handle_todo_item(
                    todo_block, 
                    line_length,
                    current_pos, 
                    current_paragraph,
                    paragraph_start,
                    line_blocks,
                    in_todo_sequence
                )
                in_todo_sequence = True
                current_pos += line_length
                continue
            
            # No longer in a todo sequence
            if in_todo_sequence:
                in_todo_sequence = False
            
            # Handle empty lines
            if not line.strip():
                self._handle_empty_line(
                    current_paragraph, 
                    paragraph_start, 
                    current_pos, 
                    line_blocks
                )
                current_paragraph = []
                current_pos += line_length
                continue
            
            # Check for other special blocks
            special_block = self._try_process_special_block(line)
            if special_block:
                self._handle_special_block(
                    special_block,
                    line_length,
                    current_pos,
                    current_paragraph,
                    paragraph_start,
                    line_blocks
                )
                current_paragraph = []
                current_pos += line_length
                continue
                
            # Handle as part of paragraph
            if not current_paragraph:
                paragraph_start = current_pos
            current_paragraph.append(line)
            current_pos += line_length
        
        # Process any remaining paragraph content
        self._process_paragraph(
            current_paragraph, paragraph_start, current_pos, line_blocks
        )
        
        return line_blocks
    
    def _is_multiline_marker(self, line: str) -> bool:
        """Check if a line is a multiline content marker."""
        return line.strip() == self.MULTILINE_CONTENT_MARKER
    
    def _is_toggle_marker(self, line: str) -> bool:
        """Check if a line is a toggle content marker."""
        return line.strip() == self.TOGGLE_MARKER
    
    def _is_spacer_marker(self, line: str) -> bool:
        """Prüft, ob eine Zeile ein Spacer-Marker ist."""
        return line.strip() == self.SPACER_MARKER
    
    def _try_process_todo_item(self, line: str) -> Optional[Dict[str, Any]]:
        """
        Try to process a line as a todo item.
        
        Returns:
            Todo block if line is a todo item, None otherwise
        """
        for element in ElementRegistry.get_elements():
            if (not element.is_multiline() and
                hasattr(element, 'match_markdown') and
                element.__name__ == 'TodoElement' and
                element.match_markdown(line)):
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
        in_todo_sequence: bool
    ) -> None:
        """Handle a todo item line."""
        # If we were building a paragraph, finish it before starting todos
        if not in_todo_sequence and current_paragraph:
            self._process_paragraph(
                current_paragraph, paragraph_start, current_pos, line_blocks
            )
            current_paragraph.clear()
        
        line_blocks.append((current_pos, current_pos + line_length, todo_block))
    
    def _handle_empty_line(
        self,
        current_paragraph: List[str],
        paragraph_start: int,
        current_pos: int,
        line_blocks: List[Tuple[int, int, Dict[str, Any]]]
    ) -> None:
        """Handle an empty line."""
        if current_paragraph:
            self._process_paragraph(
                current_paragraph, paragraph_start, current_pos, line_blocks
            )
    
    def _try_process_special_block(self, line: str) -> Optional[Dict[str, Any]]:
        """
        Try to process a line as a special block (not paragraph).
        
        Returns:
            Block if line is a special block, None otherwise
        """
        for element in ElementRegistry.get_elements():
            if (not element.is_multiline() and 
                hasattr(element, 'match_markdown') and
                element.match_markdown(line)):
                block = element.markdown_to_notion(line)
                if block and block.get("type") != "paragraph":
                    return block
        return None
    
    def _handle_special_block(
        self,
        block: Dict[str, Any],
        line_length: int,
        current_pos: int,
        current_paragraph: List[str],
        paragraph_start: int,
        line_blocks: List[Tuple[int, int, Dict[str, Any]]]
    ) -> None:
        """Handle a special block line."""
        # Process any accumulated paragraph content before adding the special block
        if current_paragraph:
            self._process_paragraph(
                current_paragraph, paragraph_start, current_pos, line_blocks
            )
        
        line_blocks.append((current_pos, current_pos + line_length, block))

    def _process_paragraph(
        self,
        paragraph_lines: List[str], 
        start_pos: int, 
        end_pos: int, 
        blocks: List[Tuple[int, int, Dict[str, Any]]]
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
            
        paragraph_text = '\n'.join(paragraph_lines)
        block = ElementRegistry.markdown_to_notion(paragraph_text)
        
        if not block:
            return
            
        blocks.append((start_pos, end_pos, block))
    
    def _process_explicit_spacing(self, blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Verarbeitet Blöcke und fügt automatische Einrückung nur hinzu, wenn kein expliziter Spacer vorhanden ist.
        
        Args:
            blocks: Liste der Notion-Blöcke
            
        Returns:
            Liste der Notion-Blöcke mit verarbeiteten Spacern
        """
        if not blocks:
            return blocks
            
        final_blocks = []
        i = 0
        
        while i < len(blocks):
            current_block = blocks[i]
            final_blocks.append(current_block)
            
            # Prüfe, ob dies ein Multiline-Element ist
            block_type = current_block.get("type")
            if self._is_multiline_block_type(block_type):
                # Prüfe, ob der nächste Block bereits ein Spacer ist
                if i + 1 < len(blocks) and self._is_empty_paragraph(blocks[i + 1]):
                    # Der nächste Block ist bereits ein Spacer, füge keinen weiteren hinzu
                    pass
                else:
                    # Kein expliziter Spacer gefunden, füge automatisch einen hinzu
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
            
        multiline_elements = ElementRegistry.get_multiline_elements()
        
        for element in multiline_elements:
            element_name = element.__name__.lower()
            if block_type in element_name:
                return True
                
            if hasattr(element, 'match_notion'):
                dummy_block = {"type": block_type}
                if element.match_notion(dummy_block):
                    return True
        
        return False
    
    def _is_empty_paragraph(self, block: Dict[str, Any]) -> bool:
        """
        Prüft, ob ein Block ein leerer Paragraph ist.
        
        Args:
            block: Der zu prüfende Block
            
        Returns:
            True, wenn es sich um einen leeren Paragraph handelt, sonst False
        """
        return (
            block.get("type") == "paragraph" and 
            (not block.get("paragraph", {}).get("rich_text") or 
             len(block.get("paragraph", {}).get("rich_text", [])) == 0)
        )
    
    def _create_empty_paragraph(self) -> Dict[str, Any]:
        """
        Create an empty paragraph block.
        
        Returns:
            Empty paragraph block dictionary
        """
        return {
            "type": "paragraph",
            "paragraph": {
                "rich_text": []
            }
        }