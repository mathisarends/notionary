import re
from typing import Dict, Any, Optional, List
from typing_extensions import override

from notionary.converters.notion_block_element import NotionBlockElement


class BookmarkElement(NotionBlockElement):
    """
    Handles conversion between Markdown bookmarks and Notion bookmark blocks.
    
    Markdown bookmark syntax:
    - [bookmark](https://example.com) - Simple bookmark with URL only
    - [bookmark](https://example.com "Title") - Bookmark with URL and title
    - [bookmark](https://example.com "Title" "Description") - Bookmark with URL, title, and description
    
    Where:
    - URL is the required bookmark URL
    - Title is an optional title (enclosed in quotes)
    - Description is an optional description (enclosed in quotes)
    """
    
    # Regex pattern for bookmark syntax with optional title and description
    PATTERN = re.compile(
        r'^\[bookmark\]\(' +                         # [bookmark]( prefix
        r'(https?://[^\s"]+)' +                      # URL (required)
        r'(?:\s+"([^"]+)")?' +                       # Optional title in quotes
        r'(?:\s+"([^"]+)")?' +                       # Optional description in quotes
        r'\)$'                                       # closing parenthesis
    )
    
    @override
    @staticmethod
    def match_markdown(text: str) -> bool:
        """Check if text is a markdown bookmark."""
        return text.strip().startswith("[bookmark]") and bool(BookmarkElement.PATTERN.match(text.strip()))
    
    @override
    @staticmethod
    def match_notion(block: Dict[str, Any]) -> bool:
        """Check if block is a Notion bookmark."""
        return block.get("type") == "bookmark"
    
    @override
    @staticmethod
    def markdown_to_notion(text: str) -> Optional[Dict[str, Any]]:
        """Convert markdown bookmark to Notion bookmark block."""
        bookmark_match = BookmarkElement.PATTERN.match(text.strip())
        if not bookmark_match:
            return None
            
        url = bookmark_match.group(1)
        title = bookmark_match.group(2)
        description = bookmark_match.group(3)
        
        bookmark_data = {
            "url": url
        }
        
        # Add caption if title or description is provided
        if title or description:
            caption = []
            
            if title:
                caption.append({"type": "text", "text": {"content": title}})
                
                # Add a separator if both title and description are provided
                if description:
                    caption.append({"type": "text", "text": {"content": " - "}})
            
            if description:
                caption.append({"type": "text", "text": {"content": description}})
                
            bookmark_data["caption"] = caption
        
        return {
            "type": "bookmark",
            "bookmark": bookmark_data
        }
    
    @override
    @staticmethod
    def notion_to_markdown(block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion bookmark block to markdown bookmark."""
        if block.get("type") != "bookmark":
            return None
            
        bookmark_data = block.get("bookmark", {})
        url = bookmark_data.get("url", "")
        
        if not url:
            return None
        
        caption = bookmark_data.get("caption", [])
        
        # Extract title and description from caption if available
        if caption:
            text_content = BookmarkElement._extract_text_content(caption)
            parts = text_content.split(" - ", 1)
            
            title = parts[0].strip() if parts else ""
            description = parts[1].strip() if len(parts) > 1 else ""
            
            if title and description:
                return f'[bookmark]({url} "{title}" "{description}")'
            elif title:
                return f'[bookmark]({url} "{title}")'
        
        # Simple bookmark with URL only
        return f'[bookmark]({url})'
    
    @override
    @staticmethod
    def is_multiline() -> bool:
        """Bookmarks are single-line elements."""
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