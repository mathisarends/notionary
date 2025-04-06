import re
from typing import Dict, Any, Optional, List, Tuple
from typing_extensions import override
from notionary.converters.elements.notion_block_element import NotionBlockElement

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
        # Handle both standard "bookmark" type and "external-bookmark" type
        return block.get("type") in ["bookmark", "external-bookmark"]
    
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
                caption.append({"type": "text", "text": {"content": title, "link": None}, 
                               "annotations": {"bold": False, "italic": False, "strikethrough": False, 
                                             "underline": False, "code": False, "color": "default"},
                               "plain_text": title, "href": None})
                
                # Add a separator if both title and description are provided
                if description:
                    caption.append({"type": "text", "text": {"content": " - ", "link": None},
                                   "annotations": {"bold": False, "italic": False, "strikethrough": False, 
                                                 "underline": False, "code": False, "color": "default"},
                                   "plain_text": " - ", "href": None})
            
            if description:
                caption.append({"type": "text", "text": {"content": description, "link": None},
                               "annotations": {"bold": False, "italic": False, "strikethrough": False, 
                                             "underline": False, "code": False, "color": "default"},
                               "plain_text": description, "href": None})
                
            bookmark_data["caption"] = caption
        else:
            # Empty caption list to match Notion's format for bookmarks without titles
            bookmark_data["caption"] = []
        
        return {
            "type": "bookmark",
            "bookmark": bookmark_data
        }
    
    @override
    @staticmethod
    def notion_to_markdown(block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion bookmark block to markdown bookmark."""
        block_type = block.get("type", "")
        
        if block_type == "bookmark":
            bookmark_data = block.get("bookmark", {})
        elif block_type == "external-bookmark":
            # Handle external-bookmark type
            # Extract URL from the external-bookmark structure
            url = block.get("url", "")
            if not url:
                return None
                
            # For external bookmarks, create a simple bookmark format
            return f'[bookmark]({url})'
        else:
            return None
            
        url = bookmark_data.get("url", "")
        
        if not url:
            return None
        
        caption = bookmark_data.get("caption", [])
        
        if not caption:
            # Simple bookmark with URL only
            return f'[bookmark]({url})'
        
        # Extract title and description from caption
        title, description = BookmarkElement._parse_caption(caption)
        
        if title and description:
            return f'[bookmark]({url} "{title}" "{description}")'
        elif title:
            return f'[bookmark]({url} "{title}")'
        else:
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
    
    @staticmethod
    def _parse_caption(caption: List[Dict[str, Any]]) -> Tuple[str, str]:
        """
        Parse Notion caption into title and description components.
        Returns a tuple of (title, description).
        """
        if not caption:
            return "", ""
            
        # Extract the full text content from caption
        full_text = BookmarkElement._extract_text_content(caption)
        
        # Check if the text contains a separator
        if " - " in full_text:
            parts = full_text.split(" - ", 1)
            return parts[0].strip(), parts[1].strip()
        else:
            # If no separator, assume the whole content is the title
            return full_text.strip(), ""
        
    @override
    @classmethod
    def get_llm_prompt_content(cls) -> dict:
        """
        Returns a dictionary with all information needed for LLM prompts about this element.
        Includes description, usage guidance, syntax options, and examples.
        """
        return {
            "description": "Creates a bookmark that links to an external website.",
            "when_to_use": "Use bookmarks when you want to reference external content while keeping the page clean and organized. Bookmarks display a preview card for the linked content.",
            "syntax": [
                "[bookmark](https://example.com) - Simple bookmark with URL only",
                "[bookmark](https://example.com \"Title\") - Bookmark with URL and title",
                "[bookmark](https://example.com \"Title\" \"Description\") - Bookmark with URL, title, and description"
            ],
            "examples": [
                '[bookmark](https://notion.so "Notion Homepage" "Your connected workspace")',
                '[bookmark](https://github.com "GitHub" "Where the world builds software")'
            ]
        }