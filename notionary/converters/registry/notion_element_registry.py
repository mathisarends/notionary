from typing import Dict, Any, Optional, List, Type
from notionary.converters.notion_block_element import NotionBlockElement

class ElementRegistry:
    """Registry of elements that can convert between Markdown and Notion."""
    
    _elements = []
    
    @classmethod
    def register(cls, element_class: Type[NotionBlockElement]):
        """Register an element class."""
        cls._elements.append(element_class)
    
    @classmethod
    def find_markdown_handler(cls, text: str) -> Optional[Type[NotionBlockElement]]:
        """Find an element that can handle the given markdown text."""
        for element in cls._elements:
            if element.match_markdown(text):
                return element
        return None
    
    @classmethod
    def find_notion_handler(cls, block: Dict[str, Any]) -> Optional[Type[NotionBlockElement]]:
        """Find an element that can handle the given Notion block."""
        for element in cls._elements:
            if element.match_notion(block):
                return element
        return None
    
    @classmethod
    def markdown_to_notion(cls, text: str) -> Optional[Dict[str, Any]]:
        """Convert markdown to Notion block using registered elements."""
        handler = cls.find_markdown_handler(text)
        if handler:
            return handler.markdown_to_notion(text)
        return None
    
    @classmethod
    def notion_to_markdown(cls, block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion block to markdown using registered elements."""
        handler = cls.find_notion_handler(block)
        if handler:
            return handler.notion_to_markdown(block)
        return None
    
    @classmethod
    def get_multiline_elements(cls) -> List[Type[NotionBlockElement]]:
        """Get all registered multiline elements."""
        return [element for element in cls._elements if element.is_multiline()]
    
    @classmethod
    def get_elements(cls) -> List[Type[NotionBlockElement]]:
        """Get all registered elements."""
        return cls._elements.copy()