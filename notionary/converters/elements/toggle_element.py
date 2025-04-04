import re
from typing import Dict, Any, Optional, List
from notionary.converters.notion_block_element import NotionBlockElement


class ToggleElement(NotionBlockElement):
    """
    Handles conversion between Markdown toggle blocks and Notion toggle blocks.
    
    Markdown toggle syntax:
    +++ Toggle title
       Indented content that belongs to the toggle
       More indented content
    
    Non-indented content marks the end of the toggle block.
    """
    
    # Regex pattern for toggle syntax
    PATTERN = re.compile(r'^[+]{3}\s+(.+)$')
    
    # Indentation pattern to detect nested content
    INDENT_PATTERN = re.compile(r'^(\s{2,}|\t+)(.+)$')
    
    @staticmethod
    def match_markdown(text: str) -> bool:
        """Check if text is a markdown toggle."""
        return bool(ToggleElement.PATTERN.match(text.strip()))
    
    @staticmethod
    def match_notion(block: Dict[str, Any]) -> bool:
        """Check if block is a Notion toggle."""
        return block.get("type") == "toggle"
    
    @staticmethod
    def markdown_to_notion(text: str) -> Optional[Dict[str, Any]]:
        """Convert markdown toggle to Notion toggle block.
        
        Note: This method only converts the toggle title line.
        The nested content needs to be processed separately.
        """
        toggle_match = ToggleElement.PATTERN.match(text.strip())
        if not toggle_match:
            return None
            
        # Extract content
        title = toggle_match.group(1)
        
        return {
            "type": "toggle",
            "toggle": {
                "rich_text": [
                    {"type": "text", "text": {"content": title}}
                ],
                "color": "default",
                "children": []  # Will be populated with nested content
            }
        }
    
    @staticmethod
    def notion_to_markdown(block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion toggle block to markdown toggle."""
        if block.get("type") != "toggle":
            return None
            
        toggle_data = block.get("toggle", {})
        
        # Extract title from rich_text
        title = ToggleElement._extract_text_content(toggle_data.get("rich_text", []))
        
        # Create the toggle line
        toggle_line = f"+++ {title}"
        
        # Process children if any
        children = toggle_data.get("children", [])
        if children:
            child_lines = []
            for child_block in children:
                # This would need to be handled by a full converter that can dispatch
                # to the appropriate element type for each child block
                child_markdown = "  [Nested content]"  # Placeholder
                child_lines.append(f"  {child_markdown}")
            
            return toggle_line + "\n" + "\n".join(child_lines)
        
        return toggle_line
    
    @staticmethod
    def is_multiline() -> bool:
        """Toggle blocks can span multiple lines due to their nested content."""
        return True
    
    @staticmethod
    def _extract_text_content(rich_text: List[Dict[str, Any]]) -> str:
        """Extract plain text content from Notion rich_text elements."""
        result = ""
        for text_obj in rich_text:
            if text_obj.get("type") == "text":
                result += text_obj.get("text", {}).get("content", "")
            elif "plain_text" in text_obj:
                result += text_obj.get("plain_text", "")
        return result