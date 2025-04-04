import re
from typing import Dict, Any, Optional
from typing_extensions import override
from notionary.converters.elements.text_formatting import parse_inline_formatting, extract_text_with_formatting
from notionary.converters.notion_block_element import NotionBlockElement


class BulletedListElement(NotionBlockElement):
    """Class for converting between Markdown bullet lists and Notion bulleted list items."""
    
    @override
    @staticmethod
    def markdown_to_notion(text: str) -> Optional[Dict[str, Any]]:
        """Convert markdown bulleted list item to Notion block."""
        pattern = re.compile(r'^(\s*)[*\-+]\s+(?!\[[ x]\])(.+)$')  # Avoid matching todo items
        list_match = pattern.match(text)
        if not list_match:
            return None
            
        content = list_match.group(2)
        
        # Use parse_inline_formatting to handle rich text
        rich_text = parse_inline_formatting(content)
        
        return {
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": rich_text,
                "color": "default"
            }
        }
    
    @override
    @staticmethod
    def notion_to_markdown(block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion bulleted list item block to markdown."""
        if block.get("type") != "bulleted_list_item":
            return None
        
        rich_text = block.get("bulleted_list_item", {}).get("rich_text", [])
        content = extract_text_with_formatting(rich_text)
        
        return f"- {content}"
    
    @override
    @staticmethod
    def match_markdown(text: str) -> bool:
        """Check if this element can handle the given markdown text."""
        pattern = re.compile(r'^(\s*)[*\-+]\s+(?!\[[ x]\])(.+)$')
        return bool(pattern.match(text))
    
    @override
    @staticmethod
    def match_notion(block: Dict[str, Any]) -> bool:
        """Check if this element can handle the given Notion block."""
        return block.get("type") == "bulleted_list_item"


class NumberedListElement:
    """Class for converting between Markdown numbered lists and Notion numbered list items."""
    
    @override
    @staticmethod
    def markdown_to_notion(text: str) -> Optional[Dict[str, Any]]:
        """Convert markdown numbered list item to Notion block."""
        pattern = re.compile(r'^\s*(\d+)\.\s+(.+)$')
        numbered_match = pattern.match(text)
        if not numbered_match:
            return None
            
        content = numbered_match.group(2)
        
        # Use parse_inline_formatting to handle rich text
        rich_text = parse_inline_formatting(content)
        
        return {
            "type": "numbered_list_item",
            "numbered_list_item": {
                "rich_text": rich_text,
                "color": "default"
            }
        }
    
    @override
    @staticmethod
    def notion_to_markdown(block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion numbered list item block to markdown."""
        if block.get("type") != "numbered_list_item":
            return None
        
        rich_text = block.get("numbered_list_item", {}).get("rich_text", [])
        content = extract_text_with_formatting(rich_text)
        
        return f"1. {content}"
    
    @override
    @staticmethod
    def match_markdown(text: str) -> bool:
        """Check if this element can handle the given markdown text."""
        pattern = re.compile(r'^\s*\d+\.\s+(.+)$')
        return bool(pattern.match(text))
    
    @override
    @staticmethod
    def match_notion(block: Dict[str, Any]) -> bool:
        """Check if this element can handle the given Notion block."""
        return block.get("type") == "numbered_list_item"
    
    @override
    @staticmethod
    def is_multiline() -> bool:
        return False