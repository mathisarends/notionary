import re
from typing import Dict, Any, Optional
from typing_extensions import override
from notionary.converters.notion_block_element import NotionBlockElement
from notionary.converters.elements.text_formatting import parse_inline_formatting, extract_text_with_formatting

class TodoElement(NotionBlockElement):
    """
    Handles conversion between Markdown todo items and Notion to_do blocks.
    
    Markdown syntax examples:
    - [ ] Unchecked todo item
    - [x] Checked todo item
    * [ ] Also works with asterisk
    + [ ] Also works with plus sign
    """
    
    # Patterns for detecting Markdown todo items
    TODO_PATTERN = re.compile(r'^\s*[-*+]\s+\[\s?\]\s+(.+)$')
    DONE_PATTERN = re.compile(r'^\s*[-*+]\s+\[x\]\s+(.+)$')
    
    @override
    @staticmethod
    def match_markdown(text: str) -> bool:
        """Check if text is a markdown todo item."""
        return bool(TodoElement.TODO_PATTERN.match(text) or TodoElement.DONE_PATTERN.match(text))
    
    @override
    @staticmethod
    def match_notion(block: Dict[str, Any]) -> bool:
        """Check if block is a Notion to_do block."""
        return block.get("type") == "to_do"
    
    @override
    @staticmethod
    def markdown_to_notion(text: str) -> Optional[Dict[str, Any]]:
        """Convert markdown todo item to Notion to_do block."""
        done_match = TodoElement.DONE_PATTERN.match(text)
        if done_match:
            content = done_match.group(1)
            return TodoElement._create_todo_block(content, True)
        
        todo_match = TodoElement.TODO_PATTERN.match(text)
        if todo_match:
            content = todo_match.group(1)
            return TodoElement._create_todo_block(content, False)
        
        return None
    
    @override
    @staticmethod
    def notion_to_markdown(block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion to_do block to markdown todo item."""
        if block.get("type") != "to_do":
            return None
        
        todo_data = block.get("to_do", {})
        checked = todo_data.get("checked", False)
        
        # Extract text content
        rich_text = todo_data.get("rich_text", [])
        content = extract_text_with_formatting(rich_text)
        
        # Format as markdown todo item
        checkbox = "[x]" if checked else "[ ]"
        return f"- {checkbox} {content}"
    
    @staticmethod
    def _create_todo_block(content: str, checked: bool) -> Dict[str, Any]:
        """
        Create a Notion to_do block.
        
        Args:
            content: The text content of the todo item
            checked: Whether the todo item is checked
            
        Returns:
            Notion to_do block dictionary
        """
        return {
            "type": "to_do",
            "to_do": {
                "rich_text": parse_inline_formatting(content),
                "checked": checked,
                "color": "default"
            }
        }
        
    @override
    @staticmethod
    def is_multiline() -> bool:
        return False