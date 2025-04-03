# File: notionary/converters/markdown_to_notion_converter.py

from typing import Dict, Any, List, Tuple
from notionary.converters.notion_element_registry import ElementRegistry

class MarkdownToNotionConverter:
    """Converts Markdown text to Notion API block format."""
    
    def __init__(self):
        """Initialize the converter."""
        pass
    
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
        
        all_blocks = multiline_blocks + line_blocks
        all_blocks.sort(key=lambda x: x[0])  # Sort by start position
        
        # Get just the blocks, without position information
        blocks = [block for _, _, block in all_blocks]
        
        # Add spacing after multiline elements
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
                    for start, end, _ in reversed(matches):
                        processed_text = processed_text[:start] + '\n' * (processed_text[start:end].count('\n')) + processed_text[end:]
        
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
        
        for line in lines:
            line_length = len(line) + 1  # +1 for newline
            
            # Handle empty lines
            if not line.strip():
                # End the current paragraph if we have one
                if current_paragraph:
                    self._process_paragraph(
                        current_paragraph, paragraph_start, current_pos, line_blocks
                    )
                    current_paragraph = []
                
                current_pos += line_length
                continue
            
            # Check if line is a special block (not paragraph)
            block = ElementRegistry.markdown_to_notion(line)
            if block and block.get("type") != "paragraph":
                # Process any accumulated paragraph content before adding the special block
                self._process_paragraph(
                    current_paragraph, paragraph_start, current_pos, line_blocks
                )
                current_paragraph = []
                
                line_blocks.append((current_pos, current_pos + line_length, block))
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
            # Check if the element name contains the block type
            # For example, "TableElement" should match "table" block type
            element_name = element.__name__.lower()
            if block_type in element_name:
                return True
                
            if hasattr(element, 'match_notion'):
                dummy_block = {"type": block_type}
                if element.match_notion(dummy_block):
                    return True
        
        return False