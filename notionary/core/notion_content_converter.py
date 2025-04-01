from typing import Awaitable, Callable, List, Dict, Any, Optional
from abc import ABC, abstractmethod
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
        text = NotionContentConverter.extract_text_with_formatting(rich_text)
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
        text = NotionContentConverter.extract_text_with_formatting(rich_text)
        return f"{self.prefix} {text}" if text else None


class BulletedListItemConverter(BlockConverter):
    """Converter for bulleted list item blocks."""
    
    def convert(self, block: Dict[str, Any]) -> Optional[str]:
        """Convert a bulleted list item to text."""
        item_data = block.get("bulleted_list_item", {})
        rich_text = item_data.get("rich_text", [])
        text = NotionContentConverter.extract_text_with_formatting(rich_text)
        return f"* {text}" if text else None


class NumberedListItemConverter(BlockConverter):
    """Converter for numbered list item blocks."""
    
    def convert(self, block: Dict[str, Any]) -> Optional[str]:
        """Convert a numbered list item to text."""
        item_data = block.get("numbered_list_item", {})
        rich_text = item_data.get("rich_text", [])
        text = NotionContentConverter.extract_text_with_formatting(rich_text)
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


class TodoConverter(BlockConverter):
    """Converter for to-do blocks."""
    
    def convert(self, block: Dict[str, Any]) -> Optional[str]:
        """Convert a to-do block to text."""
        todo_data = block.get("to_do", {})
        rich_text = todo_data.get("rich_text", [])
        text = NotionContentConverter.extract_text_with_formatting(rich_text)
        checked = todo_data.get("checked", False)
        checkbox = "[x]" if checked else "[ ]"
        return f"- {checkbox} {text}" if text else None


class QuoteConverter(BlockConverter):
    """Converter for quote blocks."""
    
    def convert(self, block: Dict[str, Any]) -> Optional[str]:
        """Convert a quote block to text."""
        quote_data = block.get("quote", {})
        rich_text = quote_data.get("rich_text", [])
        text = NotionContentConverter.extract_text_with_formatting(rich_text)
        
        if not text:
            return None
            
        # Handle multi-line quotes
        lines = text.split('\n')
        quoted_lines = [f"> {line}" for line in lines]
        
        return '\n'.join(quoted_lines)


class CalloutConverter(BlockConverter):
    """Converter for callout blocks."""
    
    def convert(self, block: Dict[str, Any]) -> Optional[str]:
        """Convert a callout block to text."""
        callout_data = block.get("callout", {})
        rich_text = callout_data.get("rich_text", [])
        text = NotionContentConverter.extract_text_with_formatting(rich_text)
        icon = callout_data.get("icon", {})
        
        if not text:
            return None
            
        # Handle the icon if present
        icon_prefix = ""
        if icon:
            emoji = icon.get("emoji", "")
            if emoji:
                icon_prefix = f"{emoji} "
        
        # Format as a blockquote with icon
        lines = text.split('\n')
        quoted_lines = [f"> {icon_prefix if i == 0 else ''}{line}" for i, line in enumerate(lines)]
        
        return '\n'.join(quoted_lines)


class TableConverter(BlockConverter):
    """Converter for table blocks."""
    
    def convert(self, block: Dict[str, Any]) -> Optional[str]:
        """
        Erstellt eine Markdown-Tabelle basierend auf den Metadaten des Table-Blocks.
        Da die Tabellendaten in Kinder-Blöcken gespeichert sind, die asynchron abgerufen werden müssten,
        erstellen wir hier eine Platzhalter-Tabelle mit der richtigen Struktur.
        """
        # Tabellendaten extrahieren
        if block.get("type") != "table":
            return None
            
        table_data = block.get("table", {})
        table_width = table_data.get("table_width", 3)
        has_column_header = table_data.get("has_column_header", False)
        
        # Header-Zeile mit angepasster Anzahl von Spalten
        header_cells = [f"Spalte {i+1}" for i in range(table_width)]
        header_row = "| " + " | ".join(header_cells) + " |"
        
        # Separator-Zeile mit der richtigen Anzahl von Spalten
        separator_row = "| " + " | ".join(["---" for _ in range(table_width)]) + " |"
        
        # Eine Platzhalterzeile für Daten
        placeholder_row = "| " + " | ".join(["..." for _ in range(table_width)]) + " |"
        
        return f"{header_row}\n{separator_row}\n{placeholder_row}"


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
        "code": CodeConverter(),
        "to_do": TodoConverter(),
        "quote": QuoteConverter(),
        "callout": CalloutConverter(),
        "table": TableConverter()
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
    def blocks_to_text(blocks: List[Dict[str, Any]], include_table_data: bool = False) -> str:
        """Convert Notion blocks to readable text.
        """
        if not blocks:
            return "Keine Inhalte gefunden."
        
        text_parts = []
        
        # Keep track of list numbering
        list_numbering = {}
        previous_block_type = None
        
        for block in blocks:
            block_type = block.get("type", "")
            converter = NotionContentConverter._converters.get(block_type)
            
            # Reset list numbering when block type changes
            if previous_block_type != block_type and block_type != "numbered_list_item":
                list_numbering = {}
            
            # Special handling for numbered lists to maintain correct numbering
            if block_type == "numbered_list_item":
                result = NotionContentConverter._handle_numbered_list_item(block, list_numbering)
                if result:
                    text_parts.append(result)
            # Special handling for tables with children data
            elif block_type == "table" and include_table_data and "children" in block:
                result = NotionContentConverter._process_table_with_children(block, block.get("children", []))
                if result:
                    text_parts.append(result)
            elif converter is None:
                logger = LoggingMixin.static_logger()
                logger.warning("Unsupported block type: %s", block_type)
                continue
            else:
                result = converter.convert(block)
                if result:
                    text_parts.append(result)
            
            previous_block_type = block_type
        
        # If we couldn't convert any blocks, return the "not found" message
        if not text_parts:
            return NotionContentConverter.CONTENT_NOT_FOUND_MSG
        
        return "\n\n".join(text_parts)
    
    @staticmethod
    def _handle_numbered_list_item(block: Dict[str, Any], list_numbering: Dict[str, int]) -> str:
        """Handle numbered list items with proper numbering."""
        item_data = block.get("numbered_list_item", {})
        rich_text = item_data.get("rich_text", [])
        text = NotionContentConverter.extract_text_with_formatting(rich_text)
        
        # Determine list level based on indentation (if available)
        # This is simplified; in a real implementation you might need more logic
        level = "level_1"  # Default to level 1
        
        if level not in list_numbering:
            list_numbering[level] = 1
        else:
            list_numbering[level] += 1
        
        number = list_numbering[level]
        
        return f"{number}. {text}" if text else None
    
    @staticmethod
    def _process_table_with_children(
        table_block: Dict[str, Any], 
        row_blocks: List[Dict[str, Any]]
    ) -> Optional[str]:
        """
        Verarbeitet einen Tabellen-Block mit seinen Kinder-Blöcken.
        """
        if not row_blocks:
            return None
            
        table_data = table_block.get("table", {})
        has_column_header = table_data.get("has_column_header", False)
        
        table_rows = []
        column_count = 0
        
        for i, row_block in enumerate(row_blocks):
            if row_block.get("type") != "table_row":
                continue
                
            row_data = row_block.get("table_row", {})
            cells = row_data.get("cells", [])
            
            if len(cells) > column_count:
                column_count = len(cells)
            
            row_texts = []
            for cell in cells:
                cell_text = NotionContentConverter.extract_text_with_formatting(cell)
                row_texts.append(cell_text or "")
            
            row = "| " + " | ".join(row_texts) + " |"
            table_rows.append(row)
        
        if not table_rows or column_count == 0:
            return None
            
        if has_column_header and len(table_rows) > 0:
            separator_row = "| " + " | ".join(["---" for _ in range(column_count)]) + " |"
            table_rows.insert(1, separator_row)
            
        return "\n".join(table_rows)
    
    @staticmethod
    def extract_text_from_rich_text(rich_text: List[Dict[str, Any]]) -> str:
        """Extract plain text from the rich_text format of Notion.
        
        Args:
            rich_text: List of rich_text objects from Notion API
            
        Returns:
            Concatenated plain text
        """
        return "".join([text.get("plain_text", "") for text in rich_text])
    
    @staticmethod
    def extract_text_with_formatting(rich_text: List[Dict[str, Any]]) -> str:
        """Extract text with Markdown formatting from rich_text format.
        
        Args:
            rich_text: List of rich_text objects from Notion API
            
        Returns:
            Formatted text in Markdown
        """
        formatted_parts = []
        
        for text_obj in rich_text:
            content = text_obj.get("plain_text", "")
            annotations = text_obj.get("annotations", {})
            
            # Apply formatting based on annotations
            if annotations.get("code", False):
                content = f"`{content}`"
            if annotations.get("bold", False):
                content = f"**{content}**"
            if annotations.get("italic", False):
                content = f"*{content}*"
            if annotations.get("strikethrough", False):
                content = f"~~{content}~~"
            if annotations.get("underline", False):
                content = f"__{content}__"
            
            # Handle links
            link_data = text_obj.get("href")
            if link_data:
                content = f"[{content}]({link_data})"
            
            formatted_parts.append(content)
        
        return "".join(formatted_parts)