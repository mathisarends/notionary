# File: notionary/converters/markdown_to_notion_converter.py

from typing import Dict, Any, List, Optional, Tuple
from notionary.converters.notion_element_registry import ElementRegistry

# TODO: Refactor this one.
class MarkdownToNotionConverter:
    """Converts Markdown text to Notion API block format."""
    MULTILINE_CONTENT_MARKER = '<!-- REMOVED_MULTILINE_CONTENT -->'
    
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
        
        processed_text, multiline_blocks = self._process_multiline_elements(markdown_text)
        
        line_blocks = self._process_text_lines(processed_text)
        
        # Combine and sort all blocks by their original position
        all_blocks = multiline_blocks + line_blocks
        all_blocks.sort(key=lambda x: x[0])  # Sort by start position
        
        blocks = [block for _, _, block in all_blocks]
        
        final_blocks = self._add_spacing_after_multiline(blocks)
        
        return final_blocks
    
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
                        processed_text = processed_text[:start] + '\n' + '<!-- REMOVED_MULTILINE_CONTENT -->\n' * num_newlines + processed_text[end:]
        
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
            if self._is_multiline_marker(line):
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
    
    def _add_spacing_after_multiline(self, blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Add spacing (empty paragraph) after multiline elements.
        
        Args:
            blocks: List of Notion blocks
            
        Returns:
            List of Notion blocks with spacing added
        """
        if not blocks:
            return blocks
            
        final_blocks = []
        
        for block in blocks:
            final_blocks.append(block)
            
            # Check if this is a multiline element type
            block_type = block.get("type")
            if self._is_multiline_block_type(block_type):
                # Add an empty paragraph for spacing
                final_blocks.append(self._create_empty_paragraph())
        
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