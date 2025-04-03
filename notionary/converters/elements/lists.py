import re
from typing import Dict, Any, Optional, List


class BulletedListElement:
    """Class for converting between Markdown bullet lists and Notion bulleted list items."""
    
    @staticmethod
    def markdown_to_notion(text: str) -> Optional[Dict[str, Any]]:
        """Convert markdown bulleted list item to Notion block."""
        pattern = re.compile(r'^(\s*)[*\-+]\s+(?!\[[ x]\])(.+)$')  # Avoid matching todo items
        list_match = pattern.match(text)
        if not list_match:
            return None
            
        content = list_match.group(2)
        
        # Create a simple rich_text element for plain text
        rich_text = [{"type": "text", "text": {"content": content}}]
        
        return {
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": rich_text
            }
        }
    
    @staticmethod
    def notion_to_markdown(block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion bulleted list item block to markdown."""
        if block.get("type") != "bulleted_list_item":
            return None
        
        rich_text = block.get("bulleted_list_item", {}).get("rich_text", [])
        content = BulletedListElement._extract_text_content(rich_text)
        
        return f"- {content}"
    
    @staticmethod
    def match_markdown(text: str) -> bool:
        """Check if this element can handle the given markdown text."""
        pattern = re.compile(r'^(\s*)[*\-+]\s+(?!\[[ x]\])(.+)$')
        return bool(pattern.match(text))
    
    @staticmethod
    def match_notion(block: Dict[str, Any]) -> bool:
        """Check if this element can handle the given Notion block."""
        return block.get("type") == "bulleted_list_item"
    
    @staticmethod
    def is_multiline() -> bool:
        return False
        
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


class NumberedListElement:
    """Class for converting between Markdown numbered lists and Notion numbered list items."""
    
    @staticmethod
    def markdown_to_notion(text: str) -> Optional[Dict[str, Any]]:
        """Convert markdown numbered list item to Notion block."""
        pattern = re.compile(r'^\s*(\d+)\.\s+(.+)$')
        numbered_match = pattern.match(text)
        if not numbered_match:
            return None
            
        content = numbered_match.group(2)
        
        # Create a simple rich_text element for plain text
        rich_text = [{"type": "text", "text": {"content": content}}]
        
        return {
            "type": "numbered_list_item",
            "numbered_list_item": {
                "rich_text": rich_text
            }
        }
    
    @staticmethod
    def notion_to_markdown(block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion numbered list item block to markdown."""
        if block.get("type") != "numbered_list_item":
            return None
        
        rich_text = block.get("numbered_list_item", {}).get("rich_text", [])
        content = NumberedListElement._extract_text_content(rich_text)
        
        # Use 1. for all numbered list items, as markdown renderers will handle proper numbering
        return f"1. {content}"
    
    @staticmethod
    def match_markdown(text: str) -> bool:
        """Check if this element can handle the given markdown text."""
        pattern = re.compile(r'^\s*\d+\.\s+(.+)$')
        return bool(pattern.match(text))
    
    @staticmethod
    def match_notion(block: Dict[str, Any]) -> bool:
        """Check if this element can handle the given Notion block."""
        return block.get("type") == "numbered_list_item"
    
    @staticmethod
    def is_multiline() -> bool:
        return False
        
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