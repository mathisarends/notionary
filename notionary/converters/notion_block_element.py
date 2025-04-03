from typing import Dict, Any, Optional
from abc import ABC

class NotionBlockElement(ABC):
    """Base class for elements that can be converted between Markdown and Notion."""
    
    @staticmethod
    def markdown_to_notion(text: str) -> Optional[Dict[str, Any]]:
        """Convert markdown to Notion block."""
    
    @staticmethod
    def notion_to_markdown(block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion block to markdown."""
    
    @staticmethod
    def match_markdown(text: str) -> bool:
        """Check if this element can handle the given markdown text."""
        return bool(NotionBlockElement.markdown_to_notion(text))
    
    @staticmethod
    def match_notion(block: Dict[str, Any]) -> bool:
        """Check if this element can handle the given Notion block."""
        return bool(NotionBlockElement.notion_to_markdown(block))
    
    @staticmethod
    def is_multiline() -> bool:
        return False