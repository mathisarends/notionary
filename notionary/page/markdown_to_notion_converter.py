from typing import Dict, Any, List, Optional, Tuple

from notionary.elements.registry.block_element_registry import BlockElementRegistry
from notionary.elements.registry.block_element_registry_builder import BlockElementRegistryBuilder


class MarkdownToNotionConverter:
    """Converts Markdown text to Notion API block format with support for nested structures."""
    
    SPACER_MARKER = "<!-- spacer -->"

    def __init__(self, block_registry: Optional[BlockElementRegistry] = None):
        """Initialize the converter with an optional custom block registry."""
        self._block_registry = block_registry or BlockElementRegistryBuilder().create_full_registry()

    def convert(self, markdown_text: str) -> List[Dict[str, Any]]:
        """Convert markdown text to Notion API block format."""
        if not markdown_text:
            return []

        # Process all blocks in order, preserving their positions
        all_blocks = []
        
        # Process toggleable elements first (both Toggle and ToggleableHeading)
        toggleable_blocks = self._identify_toggleable_blocks(markdown_text)
        if toggleable_blocks:
            all_blocks.extend(toggleable_blocks)
            
        # Process other multiline elements
        multiline_blocks = self._identify_multiline_blocks(markdown_text, toggleable_blocks)
        if multiline_blocks:
            all_blocks.extend(multiline_blocks)
            
        # Process remaining text line by line
        line_blocks = self._process_text_lines(markdown_text, toggleable_blocks + multiline_blocks)
        if line_blocks:
            all_blocks.extend(line_blocks)
            
        # Sort all blocks by their position in the text
        all_blocks.sort(key=lambda x: x[0])
        
        # Extract just the blocks without position information
        blocks = [block for _, _, block in all_blocks]
        
        # Process spacing between blocks
        return self._process_block_spacing(blocks)

    def _identify_toggleable_blocks(self, text: str) -> List[Tuple[int, int, Dict[str, Any]]]:
        """Identify all toggleable blocks (Toggle and ToggleableHeading) in the text."""
        toggleable_blocks = []
        
        # Find all toggleable elements
        toggleable_elements = []
        for element in self._block_registry.get_elements():
            if (element.is_multiline() and 
                hasattr(element, "match_markdown") and
                (element.__name__ == "ToggleElement" or element.__name__ == "ToggleableHeadingElement")):
                toggleable_elements.append(element)
                
        if not toggleable_elements:
            return []
            
        # Process each toggleable element type
        for element in toggleable_elements:
            if hasattr(element, "find_matches"):
                # Find matches with context awareness
                matches = element.find_matches(text, self.convert, context_aware=True)
                if matches:
                    toggleable_blocks.extend(matches)
                    
        return toggleable_blocks

    def _identify_multiline_blocks(
        self, text: str, exclude_blocks: List[Tuple[int, int, Dict[str, Any]]]
    ) -> List[Tuple[int, int, Dict[str, Any]]]:
        """Identify all multiline blocks (except toggleable blocks)."""
        # Get all multiline elements except toggleable ones
        multiline_elements = [
            element for element in self._block_registry.get_multiline_elements()
            if element.__name__ not in ["ToggleElement", "ToggleableHeadingElement"]
        ]
        
        if not multiline_elements:
            return []
            
        # Create set of positions to exclude
        exclude_positions = set()
        for start, end, _ in exclude_blocks:
            exclude_positions.update(range(start, end + 1))
            
        multiline_blocks = []
        for element in multiline_elements:
            if not hasattr(element, "find_matches"):
                continue
                
            # Find matches for this element
            if hasattr(element, "set_converter_callback"):
                matches = element.find_matches(text, self.convert)
            else:
                matches = element.find_matches(text)
                
            if not matches:
                continue
                
            # Add blocks that don't overlap with excluded positions
            for start, end, block in matches:
                if any(start <= i <= end for i in exclude_positions):
                    continue
                multiline_blocks.append((start, end, block))
                
        return multiline_blocks

    def _process_text_lines(
        self, text: str, exclude_blocks: List[Tuple[int, int, Dict[str, Any]]]
    ) -> List[Tuple[int, int, Dict[str, Any]]]:
        """Process text line by line, excluding already processed ranges."""
        if not text:
            return []
            
        # Create set of excluded positions
        exclude_positions = set()
        for start, end, _ in exclude_blocks:
            exclude_positions.update(range(start, end + 1))
            
        line_blocks = []
        lines = text.split("\n")
        
        current_pos = 0
        current_paragraph = []
        paragraph_start = 0
        in_todo_sequence = False
        
        for line in lines:
            line_length = len(line) + 1  # +1 for newline
            line_end = current_pos + line_length - 1
            
            # Skip excluded lines
            if any(current_pos <= pos <= line_end for pos in exclude_positions):
                current_pos += line_length
                continue
                
            # Check for spacer
            if line.strip() == self.SPACER_MARKER:
                line_blocks.append((
                    current_pos, 
                    line_end,
                    {"type": "paragraph", "paragraph": {"rich_text": []}}
                ))
                current_pos += line_length
                continue
                
            # Handle todo items
            todo_block = self._extract_todo_item(line)
            if todo_block:
                # Finish paragraph if needed
                if not in_todo_sequence and current_paragraph:
                    self._process_paragraph(
                        current_paragraph, paragraph_start, current_pos, line_blocks
                    )
                    current_paragraph = []
                
                line_blocks.append((current_pos, line_end, todo_block))
                in_todo_sequence = True
                current_pos += line_length
                continue
                
            if in_todo_sequence:
                in_todo_sequence = False
                
            # Handle empty lines
            if not line.strip():
                self._process_paragraph(
                    current_paragraph, paragraph_start, current_pos, line_blocks
                )
                current_paragraph = []
                current_pos += line_length
                continue
                
            # Handle special blocks
            special_block = self._extract_special_block(line)
            if special_block:
                self._process_paragraph(
                    current_paragraph, paragraph_start, current_pos, line_blocks
                )
                line_blocks.append((current_pos, line_end, special_block))
                current_paragraph = []
                current_pos += line_length
                continue
                
            # Handle as paragraph
            if not current_paragraph:
                paragraph_start = current_pos
            current_paragraph.append(line)
            current_pos += line_length
            
        # Process remaining paragraph
        self._process_paragraph(current_paragraph, paragraph_start, current_pos, line_blocks)
        
        return line_blocks

    def _extract_todo_item(self, line: str) -> Optional[Dict[str, Any]]:
        """Extract a todo item from a line if possible."""
        for element in self._block_registry.get_elements():
            if (not element.is_multiline() and 
                hasattr(element, "match_markdown") and 
                element.__name__ == "TodoElement" and 
                element.match_markdown(line)):
                return element.markdown_to_notion(line)
        return None

    def _extract_special_block(self, line: str) -> Optional[Dict[str, Any]]:
        """Extract a special block (not paragraph) from a line if possible."""
        for element in self._block_registry.get_elements():
            if (not element.is_multiline() and 
                hasattr(element, "match_markdown") and 
                element.match_markdown(line)):
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

    def _process_block_spacing(self, blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add spacing between blocks where needed."""
        if not blocks:
            return blocks
            
        final_blocks = []
        i = 0
        
        while i < len(blocks):
            current_block = blocks[i]
            final_blocks.append(current_block)
            
            # Skip non-multiline blocks
            if not self._is_multiline_block_type(current_block.get("type")):
                i += 1
                continue
                
            # Check if next block is already a spacer
            if i + 1 < len(blocks) and self._is_empty_paragraph(blocks[i + 1]):
                # Next block is already a spacer
                pass
            else:
                # Add automatic spacer
                final_blocks.append({"type": "paragraph", "paragraph": {"rich_text": []}})
                
            i += 1
            
        return final_blocks

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