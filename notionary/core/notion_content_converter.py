from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from notionary.core.notion_markdown_parser import NotionMarkdownParser
from notionary.util.logging_mixin import LoggingMixin

class BlockConverter(ABC):
    """Base class for converting Notion blocks to text."""
    
    @abstractmethod
    def convert(self, block: Dict[str, Any]) -> Optional[str]:
        """Convert a Notion block to text representation."""


class ParagraphConverter(BlockConverter):
    """Converter for paragraph blocks."""
    def convert(self, block: Dict[str, Any]) -> Optional[str]:
        """Convert a paragraph block to text."""
        paragraph_data = block.get("paragraph", {})
        rich_text = paragraph_data.get("rich_text", [])
        text = NotionContentConverter.extract_text_from_rich_text(rich_text)
        return text if text else None


class HeadingConverter(BlockConverter):
    """Converter for heading blocks."""
    
    def __init__(self, level: int):
        """Initialize with heading level."""
        self.level = level
        self.prefix = "#" * level
    
    def convert(self, block: Dict[str, Any]) -> Optional[str]:
        """Convert a heading block to text."""
        heading_key = f"heading_{self.level}"
        heading_data = block.get(heading_key, {})
        rich_text = heading_data.get("rich_text", [])
        text = NotionContentConverter.extract_text_from_rich_text(rich_text)
        return f"{self.prefix} {text}" if text else None


class BulletedListItemConverter(BlockConverter):
    """Converter for bulleted list item blocks."""
    
    def convert(self, block: Dict[str, Any]) -> Optional[str]:
        """Convert a bulleted list item to text."""
        item_data = block.get("bulleted_list_item", {})
        rich_text = item_data.get("rich_text", [])
        text = NotionContentConverter.extract_text_from_rich_text(rich_text)
        return f"• {text}" if text else None


class NumberedListItemConverter(BlockConverter):
    """Converter for numbered list item blocks."""
    
    def convert(self, block: Dict[str, Any]) -> Optional[str]:
        """Convert a numbered list item to text."""
        item_data = block.get("numbered_list_item", {})
        rich_text = item_data.get("rich_text", [])
        text = NotionContentConverter.extract_text_from_rich_text(rich_text)
        return f"1. {text}" if text else None


class DividerConverter(BlockConverter):
    """Converter for divider blocks."""
    
    def convert(self, block: Dict[str, Any]) -> str:
        """Convert a divider to text."""
        return "---"


class CodeConverter(BlockConverter):
    """Converter for code blocks."""
    
    def convert(self, block: Dict[str, Any]) -> Optional[str]:
        """Convert a code block to text."""
        code_data = block.get("code", {})
        rich_text = code_data.get("rich_text", [])
        text = NotionContentConverter.extract_text_from_rich_text(rich_text)
        language = code_data.get("language", "")
        return f"```{language}\n{text}\n```" if text else None


class NotionContentConverter(LoggingMixin):
    """Class for converting between Notion blocks and text formats."""
    CONTENT_NOT_FOUND_MSG = "Content not found."
    
    # Registry of block converters
    _converters: Dict[str, BlockConverter] = {
        "paragraph": ParagraphConverter(),
        "heading_1": HeadingConverter(1),
        "heading_2": HeadingConverter(2),
        "heading_3": HeadingConverter(3),
        "bulleted_list_item": BulletedListItemConverter(),
        "numbered_list_item": NumberedListItemConverter(),
        "divider": DividerConverter(),
        "code": CodeConverter()
    }
    
    @classmethod
    def get_converters(cls) -> Dict[str, BlockConverter]:
        """Get the converter registry."""
        return cls._converters
    
    @staticmethod
    def register_converter(block_type: str, converter: BlockConverter) -> None:
        """Register a new block converter.
        
        Args:
            block_type: The Notion block type (e.g., "paragraph", "heading_1")
            converter: The BlockConverter implementation
        """
        NotionContentConverter._converters[block_type] = converter
    
    @staticmethod
    def markdown_to_blocks(text: str) -> List[Dict[str, Any]]:
        """Convert Markdown text to Notion API block format.
        
        Args:
            text: Markdown text to convert
            
        Returns:
            List of Notion block objects
        """
        return NotionMarkdownParser.parse_markdown(text)
    
    @staticmethod
    def blocks_to_text(blocks: List[Dict[str, Any]]) -> str:
        """Convert Notion blocks to readable text.
        
        Args:
            blocks: List of Notion block objects
            
        Returns:
            Text representation of the blocks
        """
        if not blocks:
            return "Keine Inhalte gefunden."
        
        text_parts = []
        
        for block in blocks:
            block_type = block.get("type", "")
            converter = NotionContentConverter._converters.get(block_type)
            
            if converter is None:
                logger = LoggingMixin.static_logger()
                logger.warning("Unsupported block type: %s", block_type)
                continue
        
            result = converter.convert(block)
            
            if result:
                text_parts.append(result)
        
        # If we couldn't convert any blocks, return the "not found" message
        if not text_parts:
            return NotionContentConverter.CONTENT_NOT_FOUND_MSG
        
        return "\n\n".join(text_parts)
    
    @staticmethod
    def extract_text_from_rich_text(rich_text: List[Dict[str, Any]]) -> str:
        """Extract plain text from the rich_text format of Notion.
        
        Args:
            rich_text: List of rich_text objects from Notion API
            
        Returns:
            Concatenated plain text
        """
        return "".join([text.get("plain_text", "") for text in rich_text])