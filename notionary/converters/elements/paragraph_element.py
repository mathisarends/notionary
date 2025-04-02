# File: elements/paragraphs.py

from typing import Dict, Any, Optional

from notionary.converters.base_element import BaseElement
from notionary.converters.elements.text_formatting import extract_text_with_formatting, parse_inline_formatting

class ParagraphElement(BaseElement):
    """Handles conversion between Markdown paragraphs and Notion paragraph blocks."""
    
    @staticmethod
    def match_markdown(text: str) -> bool:
        """
        Check if text is a markdown paragraph.
        Paragraphs are essentially any text that isn't matched by other block elements.
        Since paragraphs are the fallback element, this always returns True.
        """
        return True
    
    @staticmethod
    def match_notion(block: Dict[str, Any]) -> bool:
        """Check if block is a Notion paragraph."""
        return block.get("type") == "paragraph"
    
    @staticmethod
    def markdown_to_notion(text: str) -> Optional[Dict[str, Any]]:
        """Convert markdown paragraph to Notion paragraph block."""
        if not text.strip():
            return None
            
        return {
            "type": "paragraph",
            "paragraph": {
                "rich_text": parse_inline_formatting(text)
            }
        }
    
    @staticmethod
    def notion_to_markdown(block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion paragraph block to markdown paragraph."""
        if block.get("type") != "paragraph":
            return None
            
        paragraph_data = block.get("paragraph", {})
        rich_text = paragraph_data.get("rich_text", [])
        
        text = extract_text_with_formatting(rich_text)
        return text if text else None