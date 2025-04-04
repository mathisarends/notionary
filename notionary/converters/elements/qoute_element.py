import re
from typing import Dict, Any, Optional, List, Tuple
from typing_extensions import override

from notionary.converters.notion_block_element import NotionBlockElement


class QuoteElement(NotionBlockElement):
    """Class for converting between Markdown blockquotes and Notion quote blocks with background color support."""
    
    # Mapping von Markdown-Farbnamen zu Notion-Farbnamen
    COLOR_MAPPING = {
        "gray": "gray_background",
        "brown": "brown_background",
        "orange": "orange_background",
        "yellow": "yellow_background",
        "green": "green_background",
        "blue": "blue_background", 
        "purple": "purple_background",
        "pink": "pink_background",
        "red": "red_background"
    }
    
    # Umgekehrtes Mapping für die Rückkonvertierung
    REVERSE_COLOR_MAPPING = {v: k for k, v in COLOR_MAPPING.items()}
    
    @staticmethod
    def find_matches(text: str) -> List[Tuple[int, int, Dict[str, Any]]]:
        """
        Find all blockquote matches in the text and return their positions and blocks.
        
        Args:
            text: The input markdown text
            
        Returns:
            List of tuples (start_pos, end_pos, block)
        """
        quote_pattern = re.compile(r'^\s*>\s?(.*)', re.MULTILINE)
        matches = []
        
        # Find all potential quote line matches
        quote_matches = list(quote_pattern.finditer(text))
        if not quote_matches:
            return []
        
        # Group consecutive quote lines
        i = 0
        while i < len(quote_matches):
            start_match = quote_matches[i]
            start_pos = start_match.start()
            
            # Find consecutive quote lines
            j = i + 1
            while j < len(quote_matches):
                # Check if this is the next line (considering newlines)
                if (text[quote_matches[j-1].end():quote_matches[j].start()].count('\n') == 1 or
                    # Or if it's an empty line followed by a quote line
                    (text[quote_matches[j-1].end():quote_matches[j].start()].strip() == '' and
                     text[quote_matches[j-1].end():quote_matches[j].start()].count('\n') <= 2)):
                    j += 1
                else:
                    break
                    
            end_pos = quote_matches[j-1].end()
            quote_text = text[start_pos:end_pos]
            
            # Create the block
            block = QuoteElement.markdown_to_notion(quote_text)
            if block:
                matches.append((start_pos, end_pos, block))
                
            i = j
            
        return matches
    
    @override
    @staticmethod
    def markdown_to_notion(text: str) -> Optional[Dict[str, Any]]:
        """Convert markdown blockquote to Notion block with background color support."""
        if not text:
            return None
            
        quote_pattern = re.compile(r'^\s*>\s?(.*)', re.MULTILINE)
        
        # Check if it's a blockquote
        if not quote_pattern.search(text):
            return None
            
        # Extract quote content
        lines = text.split('\n')
        quote_lines = []
        color = "default"  # Standardfarbe
        
        # Überprüfen, ob der erste Nicht-Leerzeichen-Inhalt eine Farbangabe ist
        first_line = None
        for line in lines:
            quote_match = quote_pattern.match(line)
            if quote_match and quote_match.group(1).strip():
                first_line = quote_match.group(1).strip()
                break
        
        # Farbangabe in eckigen Klammern prüfen
        if first_line:
            color_match = re.match(r'^\[background:(\w+)\]\s*(.*)', first_line)
            if color_match:
                potential_color = color_match.group(1).lower()
                if potential_color in QuoteElement.COLOR_MAPPING:
                    color = QuoteElement.COLOR_MAPPING[potential_color]
                    # Erste Zeile ohne Farbangabe neu hinzufügen
                    first_line = color_match.group(2)
        
        # Inhalte extrahieren
        processing_first_color_line = True
        for line in lines:
            quote_match = quote_pattern.match(line)
            if quote_match:
                content = quote_match.group(1)
                # Farbangabe in der ersten Zeile entfernen
                if processing_first_color_line and content.strip() and re.match(r'^\[background:(\w+)\]', content.strip()):
                    content = re.sub(r'^\[background:(\w+)\]\s*', '', content)
                    processing_first_color_line = False
                quote_lines.append(content)
            elif not line.strip() and quote_lines:
                # Allow empty lines within the quote
                quote_lines.append("")
            
        if not quote_lines:
            return None
            
        quote_content = '\n'.join(quote_lines).strip()
        
        # Create rich_text elements directly
        rich_text = [{"type": "text", "text": {"content": quote_content}}]
        
        return {
            "type": "quote",
            "quote": {
                "rich_text": rich_text,
                "color": color
            }
        }
    
    @override
    @staticmethod
    def notion_to_markdown(block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion quote block to markdown with background color support."""
        if block.get("type") != "quote":
            return None
        
        rich_text = block.get("quote", {}).get("rich_text", [])
        color = block.get("quote", {}).get("color", "default")
        
        # Extract the text content
        content = QuoteElement._extract_text_content(rich_text)
        
        # Format as markdown blockquote
        lines = content.split('\n')
        formatted_lines = []
        
        # Füge die Farbinformation zur ersten Zeile hinzu, falls nicht default
        if color != "default" and color in QuoteElement.REVERSE_COLOR_MAPPING:
            markdown_color = QuoteElement.REVERSE_COLOR_MAPPING.get(color)
            first_line = lines[0] if lines else ""
            formatted_lines.append(f"> [background:{markdown_color}] {first_line}")
            lines = lines[1:] if len(lines) > 1 else []
        
        # Füge die restlichen Zeilen hinzu
        for line in lines:
            formatted_lines.append(f"> {line}")
        
        return '\n'.join(formatted_lines)
    
    @override
    @staticmethod
    def match_markdown(text: str) -> bool:
        """Check if this element can handle the given markdown text."""
        quote_pattern = re.compile(r'^\s*>\s?(.*)', re.MULTILINE)
        return bool(quote_pattern.search(text))
    
    @override
    @staticmethod
    def match_notion(block: Dict[str, Any]) -> bool:
        """Check if this element can handle the given Notion block."""
        return block.get("type") == "quote"
    
    @override
    @staticmethod
    def is_multiline() -> bool:
        """Blockquotes can span multiple lines."""
        return True
        
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