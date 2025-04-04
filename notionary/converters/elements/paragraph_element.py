from typing import Dict, Any, Optional
from typing_extensions import override

from notionary.converters.notion_block_element import NotionBlockElement
from notionary.converters.elements.text_formatting import extract_text_with_formatting, parse_inline_formatting

class ParagraphElement(NotionBlockElement):
    """Handles conversion between Markdown paragraphs and Notion paragraph blocks."""

    @override
    @staticmethod
    def match_markdown(text: str) -> bool:
        """
        Check if text is a markdown paragraph.
        Paragraphs are essentially any text that isn't matched by other block elements.
        Since paragraphs are the fallback element, this always returns True.
        """
        return True
    
    @override
    @staticmethod
    def match_notion(block: Dict[str, Any]) -> bool:
        """Check if block is a Notion paragraph."""
        return block.get("type") == "paragraph"
    
    @override
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
    
    @override
    @staticmethod
    def notion_to_markdown(block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion paragraph block to markdown paragraph."""
        if block.get("type") != "paragraph":
            return None
            
        paragraph_data = block.get("paragraph", {})
        rich_text = paragraph_data.get("rich_text", [])
        
        text = extract_text_with_formatting(rich_text)
        return text if text else None
    
    @override
    @staticmethod
    def is_multiline() -> bool:
        return False
    
    @classmethod
    def get_llm_prompt_content(cls) -> dict:
        """Returns information for LLM prompts about this element."""
        return {
            "description": "Creates standard paragraph blocks for regular text content.",
            "when_to_use": "Use paragraphs for normal text content. Paragraphs are the default block type and will be used when no other specific formatting is applied.",
            "syntax": ["Just write text normally without any special prefix"],
            "notes": ["Paragraphs support inline formatting like **bold**, *italic*, ~~strikethrough~~, `code`, and [links](url)"],
            "examples": ["This is a simple paragraph with plain text.", 
                        "This paragraph has **bold** and *italic* formatting."]
        }