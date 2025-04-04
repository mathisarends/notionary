# File: elements/dividers.py

from typing import Dict, Any, Optional
from typing_extensions import override
import re
from notionary.converters.notion_block_element import NotionBlockElement

class DividerElement(NotionBlockElement):
    """
    Handles conversion between Markdown horizontal dividers and Notion divider blocks.
    
    Markdown divider syntax:
    - Three or more hyphens (---) on a line by themselves
    """
    
    PATTERN = re.compile(r'^\s*-{3,}\s*$')
    
    @override
    @staticmethod
    def match_markdown(text: str) -> bool:
        """Check if text is a markdown divider."""
        return bool(DividerElement.PATTERN.match(text))
    
    @override
    @staticmethod
    def match_notion(block: Dict[str, Any]) -> bool:
        """Check if block is a Notion divider."""
        return block.get("type") == "divider"
    
    @override
    @staticmethod
    def markdown_to_notion(text: str) -> Optional[Dict[str, Any]]:
        """Convert markdown divider to Notion divider block."""
        if not DividerElement.match_markdown(text):
            return None
            
        return {
            "type": "divider",
            "divider": {}
        }
    
    @override
    @staticmethod
    def notion_to_markdown(block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion divider block to markdown divider."""
        if block.get("type") != "divider":
            return None
            
        return "---"
    
    @override
    @staticmethod
    def is_multiline() -> bool:
        return False