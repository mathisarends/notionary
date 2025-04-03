# File: notionary/converters/markdown_to_notion_converter.py

from typing import Dict, Any, List, Tuple
from notionary.converters.notion_element_registry import ElementRegistry

class MarkdownToNotionConverter:
    """Converts Markdown text to Notion API block format."""
    
    @staticmethod
    def convert(markdown_text: str) -> List[Dict[str, Any]]:
        """
        Convert markdown text to Notion API block format.
        
        Args:
            markdown_text: The markdown text to convert
            
        Returns:
            List of Notion blocks
        """
        if not markdown_text:
            return []
        
        print("elem,elements:", ElementRegistry._elements)
        
        # Process multiline elements first (tables, code blocks, etc.)
        processed_text, multiline_blocks = MarkdownToNotionConverter._process_multiline_elements(markdown_text)
        
        line_blocks = MarkdownToNotionConverter._process_text_lines(processed_text)
        
        # Combine and sort all blocks by their original position
        all_blocks = multiline_blocks + line_blocks
        all_blocks.sort(key=lambda x: x[0])  # Sort by start position
        
        # Return just the blocks, without position information
        return [block for _, _, block in all_blocks]
    
    @staticmethod
    def _process_multiline_elements(text: str) -> Tuple[str, List[Tuple[int, int, Dict[str, Any]]]]:
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
    
    @staticmethod
    def _process_text_lines(text: str) -> List[Tuple[int, int, Dict[str, Any]]]:
        """
        Process text line by line for single-line elements.
        
        Args:
            text: The text to process
            
        Returns:
            List of (start_pos, end_pos, block) tuples
        """
        line_blocks = []
        lines = text.split('\n')
        
        current_pos = 0
        current_paragraph = []
        paragraph_start = 0
        
        for line in lines:
            line_length = len(line) + 1  # +1 for newline
            
            if not line.strip():
                # End of paragraph
                if current_paragraph:
                    paragraph_text = '\n'.join(current_paragraph)
                    block = ElementRegistry.markdown_to_notion(paragraph_text)
                    if block:
                        line_blocks.append((paragraph_start, current_pos, block))
                    current_paragraph = []
            else:
                block = ElementRegistry.markdown_to_notion(line)
                
                if block and block.get("type") != "paragraph":
                    line_blocks.append((current_pos, current_pos + line_length, block))
                else:
                    if not current_paragraph:
                        paragraph_start = current_pos
                    current_paragraph.append(line)
            
            current_pos += line_length
        
        if current_paragraph:
            paragraph_text = '\n'.join(current_paragraph)
            block = ElementRegistry.markdown_to_notion(paragraph_text)
            if block:
                line_blocks.append((paragraph_start, current_pos, block))
        
        return line_blocks