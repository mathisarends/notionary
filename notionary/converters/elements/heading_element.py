from typing import Dict, Any, Optional
from typing_extensions import override
import re

from notionary.converters.notion_block_element import NotionBlockElement
from notionary.converters.elements.text_formatting import extract_text_with_formatting, parse_inline_formatting

class HeadingElement(NotionBlockElement):
    """Handles conversion between Markdown headings and Notion heading blocks."""
    
    PATTERN = re.compile(r'^(#{1,6})\s(.+)$')
    
    @override
    @staticmethod
    def match_markdown(text: str) -> bool:
        """Check if text is a markdown heading."""
        return bool(HeadingElement.PATTERN.match(text))
    
    @override
    @staticmethod
    def match_notion(block: Dict[str, Any]) -> bool:
        """Check if block is a Notion heading."""
        block_type: str = block.get("type", "")
        return block_type.startswith("heading_") and block_type[-1] in "123456"
    
    @override
    @staticmethod
    def markdown_to_notion(text: str) -> Optional[Dict[str, Any]]:
        """Convert markdown heading to Notion heading block."""
        header_match = HeadingElement.PATTERN.match(text)
        if not header_match:
            return None
            
        level = len(header_match.group(1))
        content = header_match.group(2)
        
        # Import here to avoid circular imports
        
        return {
            "type": f"heading_{level}",
            f"heading_{level}": {
                "rich_text": parse_inline_formatting(content)
            }
        }
    
    @override
    @staticmethod
    def notion_to_markdown(block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion heading block to markdown heading."""
        block_type = block.get("type", "")
        
        if not block_type.startswith("heading_"):
            return None
            
        try:
            level = int(block_type[-1])
            if not 1 <= level <= 6:
                return None
        except ValueError:
            return None
            
        heading_data = block.get(block_type, {})
        rich_text = heading_data.get("rich_text", [])
        
        text = extract_text_with_formatting(rich_text)
        prefix = "#" * level
        return f"{prefix} {text or ''}"
    
    @override
    @staticmethod
    def is_multiline() -> bool:
        return False