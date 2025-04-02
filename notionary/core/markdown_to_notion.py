import re
from typing import List, Dict, Any, Tuple, Optional
from abc import ABC, abstractmethod


class MarkdownElementParser(ABC):
    """Base class for parsing specific markdown elements."""
    
    @abstractmethod
    def match(self, text: str) -> bool:
        """Check if this parser can handle the given text."""
        
    @abstractmethod
    def parse(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse the text into a Notion block structure."""
    
    @property
    def is_multiline(self) -> bool:
        """
        Indicates if this parser handles elements that span multiple lines.
        Default is False (single-line elements).
        """
        return False


class HeadingParser(MarkdownElementParser):
    """Parser for markdown headers (#, ##, etc.)."""
    
    def __init__(self):
        self.pattern = re.compile(r'^(#{1,6})\s(.+)$')
    
    def match(self, text: str) -> bool:
        """Check if text is a header."""
        return bool(self.pattern.match(text))
    
    def parse(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse a header line into a Notion heading block."""
        header_match = self.pattern.match(text)
        if not header_match:
            return None
            
        level = len(header_match.group(1))
        content = header_match.group(2)
        return {
            "type": f"heading_{level}",
            f"heading_{level}": {
                "rich_text": MarkdownToNotionConverter.parse_inline_formatting(content)
            }
        }
        
class ToggleParser(MarkdownElementParser):
    """Parser for simple toggle blocks in markdown (>> Toggle content)."""
    
    def __init__(self):
        self.pattern = re.compile(r'^>{2}\s+(.+)$')
    
    def match(self, text: str) -> bool:
        """Check if text is a toggle block."""
        return bool(self.pattern.match(text))
    
    def parse(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse a toggle line into a Notion toggle block."""
        toggle_match = self.pattern.match(text)
        if not toggle_match:
            return None
            
        # Extract content
        content = toggle_match.group(1)
        
        return {
            "type": "toggle",
            "toggle": {
                "rich_text": MarkdownToNotionConverter.parse_inline_formatting(content),
                "color": "default",
                "children": []  # Will be populated with nested content
            }
        }
    
    @property
    def is_multiline(self) -> bool:
        """Toggle blocks can span multiple lines due to their nested content."""
        return True


class BulletListParser(MarkdownElementParser):
    """Parser for bullet list items (*, -, +)."""
    
    def __init__(self):
        self.pattern = re.compile(r'^(\s*)[*\-+]\s(.+)$')
    
    def match(self, text: str) -> bool:
        """Check if text is a bullet list item."""
        return bool(self.pattern.match(text))
    
    def parse(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse a bullet list item into a Notion bulleted_list_item block."""
        list_match = self.pattern.match(text)
        if not list_match:
            return None
            
        content = list_match.group(2)
        return {
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": MarkdownToNotionConverter.parse_inline_formatting(content)
            }
        }


class NumberedListParser(MarkdownElementParser):
    """Parser for numbered list items (1., 2., etc.)."""
    
    def __init__(self):
        self.pattern = re.compile(r'^\s*\d+\.\s(.+)$')
    
    def match(self, text: str) -> bool:
        """Check if text is a numbered list item."""
        return bool(self.pattern.match(text))
    
    def parse(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse a numbered list item into a Notion numbered_list_item block."""
        numbered_match = self.pattern.match(text)
        if not numbered_match:
            return None
            
        content = numbered_match.group(1)
        return {
            "type": "numbered_list_item",
            "numbered_list_item": {
                "rich_text": MarkdownToNotionConverter.parse_inline_formatting(content)
            }
        }


class InlineCodeParser(MarkdownElementParser):
    """Parser for inline code (`code`)."""
    
    def __init__(self):
        self.pattern = re.compile(r'`([^`]+)`')
    
    def match(self, text: str) -> bool:
        """Check if text contains inline code."""
        return bool(self.pattern.search(text))
    
    def parse(self, text: str) -> Optional[Dict[str, Any]]:
        """
        This parser doesn't create a block, but is used during inline formatting.
        It's included here for completeness.
        """
        # Inline code is handled by the inline formatting parser
        return None


class CodeBlockParser(MarkdownElementParser):
    """Parser for multi-line code blocks (```language\ncode```)."""
    
    def __init__(self):
        self.pattern = re.compile(r'```(\w*)\n([\s\S]+?)```', re.MULTILINE)
    
    def match(self, text: str) -> bool:
        """Check if text contains a code block."""
        return bool(self.pattern.search(text))
    
    @property
    def is_multiline(self) -> bool:
        """Code blocks span multiple lines."""
        return True
    
    def parse(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Parse a code block into a Notion code block.
        This is a simplified version that doesn't return positions.
        """
        match = self.pattern.search(text)
        if not match:
            return None
            
        language = match.group(1) or "plain text"
        content = match.group(2)
        
        # Remove trailing newline if present to avoid extra blank line
        if content.endswith('\n'):
            content = content[:-1]
            
        return {
            "type": "code",
            "code": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": content
                        },
                        "annotations": MarkdownToNotionConverter.default_annotations()
                    }
                ],
                "language": language
            }
        }
    
    def find_matches(self, text: str) -> List[Tuple[int, int, Dict[str, Any]]]:
        """
        Find all code block matches in the text and return their positions.
        
        Args:
            text: The text to search in
            
        Returns:
            List of tuples with (start_pos, end_pos, block)
        """
        matches = []
        for match in self.pattern.finditer(text):
            language = match.group(1) or "plain text"
            content = match.group(2)
            
            # Remove trailing newline if present
            if content.endswith('\n'):
                content = content[:-1]
                
            block = {
                "type": "code",
                "code": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": content
                            },
                            "annotations": MarkdownToNotionConverter.default_annotations()
                        }
                    ],
                    "language": language
                }
            }
            
            matches.append((match.start(), match.end(), block))
            
        return matches


class ParagraphParser(MarkdownElementParser):
    """Default parser for paragraphs (any text)."""
    
    def match(self, text: str) -> bool:
        """Any text can be parsed as a paragraph."""
        return True
    
    def parse(self, text: str) -> Dict[str, Any]:
        """Parse text into a Notion paragraph block."""
        return {
            "type": "paragraph",
            "paragraph": {
                "rich_text": MarkdownToNotionConverter.parse_inline_formatting(text)
            }
        }
        
class TableParser(MarkdownElementParser):
    """Parser für Markdown-Tabellen."""
    
    def __init__(self):
        self.row_pattern = re.compile(r'^\s*\|(.+)\|\s*$')
        self.separator_pattern = re.compile(r'^\s*\|([\s\-:|]+)\|\s*$')
    
    def match(self, text: str) -> bool:
        """Prüft, ob ein Text eine Markdown-Tabelle enthält."""
        lines = text.split('\n')
        
        if len(lines) < 3:
            return False
        
        for i, line in enumerate(lines[:-2]):
            if (self.row_pattern.match(line) and 
                self.separator_pattern.match(lines[i+1]) and 
                self.row_pattern.match(lines[i+2])):
                return True
                
        return False
    
    @property
    def is_multiline(self) -> bool:
        """Tabellen erstrecken sich über mehrere Zeilen."""
        return True
    
    def parse(self, text: str) -> Optional[Dict[str, Any]]:
        """Konvertiert Markdown-Tabelle in Notion-Tabellenblock."""
        lines = text.split('\n')
        
        table_start = self._find_table_start(lines)
        if table_start is None:
            return None
        
        table_end = self._find_table_end(lines, table_start)
        table_lines = lines[table_start:table_end]
        
        rows = self._extract_table_rows(table_lines)
        if not rows:
            return None
            
        column_count = len(rows[0])
        self._normalize_row_lengths(rows, column_count)
        
        return {
            "type": "table",
            "table": {
                "table_width": column_count,
                "has_column_header": True,
                "has_row_header": False,
                "children": self._create_table_rows(rows)
            }
        }
    
    def _find_table_start(self, lines: List[str]) -> Optional[int]:
        """Findet den Beginn einer Tabelle in den Zeilen."""
        for i in range(len(lines) - 2):
            if (self.row_pattern.match(lines[i]) and 
                self.separator_pattern.match(lines[i+1]) and 
                self.row_pattern.match(lines[i+2])):
                return i
        return None
    
    def _find_table_end(self, lines: List[str], start_idx: int) -> int:
        """Findet das Ende einer Tabelle, beginnend ab start_idx."""
        end_idx = start_idx + 3  # Minimum: Header, Separator, eine Datenzeile
        while end_idx < len(lines) and self.row_pattern.match(lines[end_idx]):
            end_idx += 1
        return end_idx
    
    def _extract_table_rows(self, table_lines: List[str]) -> List[List[str]]:
        """Extrahiert Zeileninhalte aus Tabellenzeilen, ohne Separator-Zeile."""
        rows = []
        for i, line in enumerate(table_lines):
            if i != 1 and self.row_pattern.match(line):  # Überspringe Separator-Zeile
                cells = self._parse_table_row(line)
                if cells:
                    rows.append(cells)
        return rows
    
    def _normalize_row_lengths(self, rows: List[List[str]], column_count: int) -> None:
        """Normalisiert die Zeilenlängen auf die angegebene Spaltenanzahl."""
        for row in rows:
            if len(row) < column_count:
                row.extend([""] * (column_count - len(row)))
            elif len(row) > column_count:
                del row[column_count:]
    
    def _parse_table_row(self, row_text: str) -> List[str]:
        """Konvertiert Tabellenzeilen-Text in Zelleninhalte."""
        row_content = row_text.strip()
        
        if row_content.startswith('|'):
            row_content = row_content[1:]
        if row_content.endswith('|'):
            row_content = row_content[:-1]
            
        return [cell.strip() for cell in row_content.split('|')]
    
    def _create_table_rows(self, rows: List[List[str]]) -> List[Dict[str, Any]]:
        """Erzeugt Notion-Tabellenzeilen aus Zelleninhalten."""
        table_rows = []
        
        for row in rows:
            cells_data = []
            
            for cell_content in row:
                rich_text = MarkdownToNotionConverter.parse_inline_formatting(cell_content)
                
                if not rich_text:
                    rich_text = [{
                        "type": "text",
                        "text": {"content": ""},
                        "annotations": MarkdownToNotionConverter.default_annotations(),
                        "plain_text": "",
                        "href": None
                    }]
                    
                cells_data.append(rich_text)
                
            table_rows.append({
                "type": "table_row",
                "table_row": {
                    "cells": cells_data
                }
            })
            
        return table_rows
    
    def find_matches(self, text: str) -> List[Tuple[int, int, Dict[str, Any]]]:
        """Findet alle Tabellen im Text und gibt ihre Positionen zurück."""
        matches = []
        lines = text.split('\n')
        
        i = 0
        while i < len(lines) - 2:
            if (self.row_pattern.match(lines[i]) and 
                self.separator_pattern.match(lines[i+1]) and 
                self.row_pattern.match(lines[i+2])):
                
                start_line = i
                end_line = self._find_table_end(lines, start_line)
                
                start_pos = self._calculate_position(lines, 0, start_line)
                end_pos = start_pos + self._calculate_position(lines, start_line, end_line)
                
                table_text = '\n'.join(lines[start_line:end_line])
                table_block = self.parse(table_text)
                
                if table_block:
                    matches.append((start_pos, end_pos, table_block))
                
                i = end_line
            else:
                i += 1
                
        return matches
    
    def _calculate_position(self, lines: List[str], start: int, end: int) -> int:
        """Berechnet die Textposition in Zeichen von Zeile start bis end."""
        position = 0
        for i in range(start, end):
            position += len(lines[i]) + 1
        return position
    

class QuoteParser(MarkdownElementParser):
    """Parser für Markdown-Blockzitate (> Zitat)."""
    
    def __init__(self):
        self.quote_pattern = re.compile(r'^\s*>\s?(.*)')
    
    def match(self, text: str) -> bool:
        """Prüft, ob der Text ein Blockzitat enthält."""
        lines = text.split('\n')
        for line in lines:
            if self.quote_pattern.match(line):
                return True
        return False
    
    @property
    def is_multiline(self) -> bool:
        """Blockzitate können mehrere Zeilen umfassen."""
        return True
    
    def parse(self, text: str) -> Optional[Dict[str, Any]]:
        """Konvertiert ein Markdown-Blockzitat in einen Notion-Quote-Block."""
        lines = text.split('\n')
        quote_lines = []
        
        for line in lines:
            quote_match = self.quote_pattern.match(line)
            if quote_match:
                content = quote_match.group(1)
                quote_lines.append(content)
            elif not line.strip() and quote_lines:
                quote_lines.append("")
            elif quote_lines:
                break
        
        if not quote_lines:
            return None
            
        quote_content = '\n'.join(quote_lines).strip()
        
        return {
            "type": "quote",
            "quote": {
                "rich_text": MarkdownToNotionConverter.parse_inline_formatting(quote_content)
            }
        }
    
    def find_matches(self, text: str) -> List[Tuple[int, int, Dict[str, Any]]]:
        """Findet alle Blockzitate im Text und gibt ihre Positionen zurück."""
        matches = []
        lines = text.split('\n')
        
        i = 0
        while i < len(lines):
            if self.quote_pattern.match(lines[i]):
                start_line = i
                
                end_line = start_line + 1
                while end_line < len(lines):
                    if self.quote_pattern.match(lines[end_line]):
                        end_line += 1
                    elif not lines[end_line].strip():
                        if end_line + 1 < len(lines) and self.quote_pattern.match(lines[end_line + 1]):
                            end_line += 1
                        else:
                            break
                    else:
                        break
                
                start_pos = sum(len(lines[j]) + 1 for j in range(start_line))
                end_pos = sum(len(lines[j]) + 1 for j in range(end_line))
                
                quote_text = '\n'.join(lines[start_line:end_line])
                
                block = self.parse(quote_text)
                
                if block:
                    matches.append((start_pos, end_pos, block))
                
                i = end_line
            else:
                i += 1
        
        return matches
    
class CalloutParser(MarkdownElementParser):
    """Parser for callout blocks in markdown (!> [emoji] Callout text)."""
    
    def __init__(self):
        # Pattern for callouts: !> [emoji] Text or !> {color} [emoji] Text or !> Text
        # Group 1: Optional color in {}
        # Group 2: Optional emoji in []
        # Group 3: Callout text
        self.pattern = re.compile(r'^!>\s+(?:(?:{([a-z_]+)})?\s*)?(?:\[([^\]]+)\])?\s*(.+)$')
        
        # Default values if not specified
        self.default_emoji = "💡"
        self.default_color = "gray_background"
        
        # Valid color options in Notion
        self.valid_colors = [
            "default", "gray", "brown", "orange", "yellow", "green", "blue", 
            "purple", "pink", "red", "gray_background", "brown_background", 
            "orange_background", "yellow_background", "green_background", 
            "blue_background", "purple_background", "pink_background", "red_background"
        ]
    
    def match(self, text: str) -> bool:
        """Check if text is a callout block."""
        # Simple check before applying regex
        return text.strip().startswith("!>") and bool(self.pattern.match(text))
    
    def parse(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse a callout line into a Notion callout block."""
        callout_match = self.pattern.match(text)
        if not callout_match:
            return None
            
        # Extract components
        color = callout_match.group(1)
        emoji = callout_match.group(2)
        content = callout_match.group(3)
        
        # Set defaults if not provided
        if not emoji:
            emoji = self.default_emoji
            
        if not color or color not in self.valid_colors:
            color = self.default_color
            
        # Create the callout block
        return {
            "type": "callout",
            "callout": {
                "rich_text": MarkdownToNotionConverter.parse_inline_formatting(content),
                "icon": {
                    "type": "emoji",
                    "emoji": emoji
                },
                "color": color
            }
        }


class MarkdownToNotionConverter:
    """
    Converts Markdown text to Notion API block format.
    Provides a clean API for converting markdown content to blocks
    that can be used with the Notion API.
    """
    
    def __init__(self):
        """Initialize the converter with element parsers."""
        self.element_parsers = [
            CodeBlockParser(),
            TableParser(),
            QuoteParser(),
            HeadingParser(),
            ToggleParser(),
            CalloutParser(),
            TodoParser(),
            BulletListParser(),
            NumberedListParser(),
            InlineCodeParser(),
            ParagraphParser()
        ]
    
    def convert(self, markdown_text: str) -> List[Dict[str, Any]]:
        """
        Convert markdown text to Notion API block format.
        """
        if not markdown_text:
            return []
        
        has_toggle = any(line.strip().startswith('>>') 
                       for line in markdown_text.split('\n') 
                       if line.strip())
        
        if has_toggle:
            toggle_processor = ToggleContentProcessor()
            return toggle_processor.process_toggle_content(markdown_text, self)
        
        return self._convert_without_toggles(markdown_text)
    
    def _convert_without_toggles(self, markdown_text: str) -> List[Dict[str, Any]]:
        """
        Convert markdown text to Notion API block format without toggle processing.
        Used for regular content and for content inside toggles.
        """
        if not markdown_text:
            return []
            
        segments = self._find_segments(markdown_text)
        blocks = self._process_segments(segments)
        
        return [b for b in blocks if b is not None]
    

    def _find_segments(self, markdown_text: str) -> List[Tuple[str, Any]]:
        """
        Find all special segments and text segments in the markdown.
        """
        special_matches = self._find_special_matches(markdown_text)
        
        return self._split_into_segments(markdown_text, special_matches)
    

    def _find_special_matches(self, markdown_text: str) -> List[Tuple[int, int, str, Dict[str, Any]]]:
        """
        Find all multiline elements like tables, code blocks, and quotes.
        
        Args:
            markdown_text: The markdown text to process
            
        Returns:
            List of (start_pos, end_pos, segment_type, block) tuples
        """
        multiline_parsers = [p for p in self.element_parsers if p.is_multiline]
        special_matches = []
        
        for parser in multiline_parsers:
            if not hasattr(parser, 'find_matches') or not parser.match(markdown_text):
                continue
                
            try:
                matches = parser.find_matches(markdown_text)
                
                if isinstance(parser, TableParser):
                    parser_type = "table"
                elif isinstance(parser, CodeBlockParser):
                    parser_type = "code_block"
                elif isinstance(parser, QuoteParser):
                    parser_type = "quote"
                else:
                    parser_type = "unknown"
                
                for start, end, block in matches:
                    special_matches.append((start, end, parser_type, block))
                    
            except Exception as e:
                print(f"Error finding matches with {parser.__class__.__name__}: {e}")
        
        return sorted(special_matches, key=lambda m: m[0])
    

    def _split_into_segments(self, markdown_text: str, special_matches: List[Tuple[int, int, str, Dict[str, Any]]]) -> List[Tuple[str, Any]]:
        """
        Split text into segments based on special matches.
        """
        segments = []
        last_end = 0
        
        for start, end, segment_type, block in special_matches:
            if start > last_end:
                segments.append(("text", markdown_text[last_end:start]))
            
            segments.append((segment_type, block))
            
            last_end = end
        
        if last_end < len(markdown_text):
            segments.append(("text", markdown_text[last_end:]))
        
        return segments
    
    def _process_segments(self, segments: List[Tuple[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process each segment and generate Notion blocks.
        """
        blocks = []
        
        for segment_type, content in segments:
            if segment_type == "text":
                text_blocks = self._process_text_segment(content)
                blocks.extend(text_blocks)
            elif segment_type in ["code_block", "table", "quote"]:
                blocks.append(content)
        
        return blocks
    
    def _process_text_segment(self, text: str) -> List[Dict[str, Any]]:
        """
        Process a text segment line by line to identify block types.
        """
        segment_blocks = []
        paragraph_lines = []
        
        for line in text.split('\n'):
            if not line.strip() and paragraph_lines:
                paragraph_text = '\n'.join(paragraph_lines)
                segment_blocks.append(ParagraphParser().parse(paragraph_text))
                paragraph_lines = []
                continue
                
            if not line.strip():
                continue
                
            # Try each parser to find a match (skip multi-line parsers here)
            block = self._parse_line(line)
            
            # If it's a special block (not paragraph) and we have paragraph lines,
            # process the paragraph first
            if block["type"] != "paragraph" and paragraph_lines:
                paragraph_text = '\n'.join(paragraph_lines)
                segment_blocks.append(ParagraphParser().parse(paragraph_text))
                paragraph_lines = []
                segment_blocks.append(block)
            elif block["type"] != "paragraph":
                segment_blocks.append(block)
            else:
                paragraph_lines.append(line)
        
        if paragraph_lines:
            paragraph_text = '\n'.join(paragraph_lines)
            segment_blocks.append(ParagraphParser().parse(paragraph_text))
            
        return segment_blocks
    
    def _parse_line(self, line: str) -> Dict[str, Any]:
        """
        Parse a single line to determine its block type.
        """
        for parser in self.element_parsers:
            if parser.is_multiline or isinstance(parser, InlineCodeParser):
                continue
                
            if parser.match(line):
                block = parser.parse(line)
                if block:
                    return block
                    
        return ParagraphParser().parse(line)
    
    @staticmethod
    def parse_inline_formatting(text: str) -> List[Dict[str, Any]]:
        """Parse inline text formatting (bold, italic, code, highlight, etc.)"""
        if not text:
            return []

        elements = []
        segments = TextFormattingParser.split_text_into_segments(text)
        
        for segment in segments:
            element = MarkdownToNotionConverter._create_text_element(segment)
            if element:
                elements.append(element)
                
        return elements

    @staticmethod
    def _create_text_element(segment: Tuple[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a Notion text element from a segment.
        """
        text, formatting = segment
        
        if 'url' in formatting:
            return {
                "type": "text",
                "text": {
                    "content": text,
                    "link": {"url": formatting['url']}
                },
                "annotations": MarkdownToNotionConverter.default_annotations(),
                "plain_text": text
            }
            
        annotations = MarkdownToNotionConverter.default_annotations()
        
        # Handle special color formatting
        if 'color' in formatting:
            annotations['color'] = formatting['color']
        else:
            # Apply standard annotations (bold, italic, etc.)
            for key in formatting:
                if key in annotations:
                    annotations[key] = formatting[key]
        
        return {
            "type": "text",
            "text": {"content": text},
            "annotations": annotations,
            "plain_text": text
        }

    
    @staticmethod
    def default_annotations() -> Dict[str, bool]:
        """
        Create default annotations object.
        
        Returns:
            Default Notion text annotations
        """
        return {
            "bold": False,
            "italic": False,
            "strikethrough": False,
            "underline": False,
            "code": False,
            "color": "default"
        }
        
class TodoParser(MarkdownElementParser):
    """Parser für Markdown-Aufgabenlisten (- [ ] und - [x])."""
    
    def __init__(self):
        self.todo_pattern = re.compile(r'^\s*[-*+]\s+\[\s?\]\s+(.+)$')
        self.done_pattern = re.compile(r'^\s*[-*+]\s+\[x\]\s+(.+)$')
    
    def match(self, text: str) -> bool:
        lines = text.split('\n')
        for line in lines:
            if self.todo_pattern.match(line) or self.done_pattern.match(line):
                return True
        return False
    
    def parse(self, text: str) -> Optional[Dict[str, Any]]:
        done_match = self.done_pattern.match(text)
        if done_match:
            content = done_match.group(1)
            return self._create_todo_block(content, True)
        
        todo_match = self.todo_pattern.match(text)
        if todo_match:
            content = todo_match.group(1)
            return self._create_todo_block(content, False)
        
        return None
    
    def _create_todo_block(self, content: str, checked: bool) -> Dict[str, Any]:
        return {
            "type": "to_do",
            "to_do": {
                "rich_text": MarkdownToNotionConverter.parse_inline_formatting(content),
                "checked": checked
            }
        }
        
        
class TextFormattingParser:
    """
    Helper class for parsing inline text formatting in markdown.
    This class breaks down the complex task of parsing inline formatting
    into smaller, more manageable methods.
    """
    
    # Update the FORMAT_PATTERNS to include highlighting syntax
    FORMAT_PATTERNS = [
        (r'\*\*(.+?)\*\*', {'bold': True}),
        (r'\*(.+?)\*', {'italic': True}),
        (r'_(.+?)_', {'italic': True}),
        (r'__(.+?)__', {'underline': True}),
        (r'~~(.+?)~~', {'strikethrough': True}),
        (r'`(.+?)`', {'code': True}),  # Inline code
        (r'\[(.+?)\]\((.+?)\)', {'link': True}),
        # New pattern for highlighted text with color specification
        (r'==([a-z_]+):(.+?)==', {'highlight': True}),  # ==yellow:highlighted text==
        # Simple highlight pattern with default yellow
        (r'==(.+?)==', {'highlight_default': True}),  # ==highlighted text==
    ]
    
    @classmethod
    def split_text_into_segments(cls, text: str) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Split text into segments by formatting markers.
        
        Args:
            text: Text to split
            
        Returns:
            List of (text, formatting) tuples
        """
        if not text:
            return []
            
        segments = []
        current_pos = 0
        
        while current_pos < len(text):
            next_format = cls._find_next_format(text, current_pos)
            
            if next_format is None:
                if current_pos < len(text):
                    segments.append((text[current_pos:], {}))
                break
                
            match, formatting, start_pos = next_format
            
            if start_pos > current_pos:
                segments.append((text[current_pos:start_pos], {}))
            
            formatted_segment = cls._process_formatted_segment(match, formatting)
            segments.append(formatted_segment)
            
            current_pos = start_pos + len(match.group(0))
            
        return segments
    
    @classmethod
    def _find_next_format(cls, text: str, current_pos: int) -> Optional[Tuple[re.Match, Dict[str, Any], int]]:
        """
        Find the next formatting marker in the text.
        
        Args:
            text: The text to search in
            current_pos: Current position in the text
            
        Returns:
            Tuple of (match object, formatting dict, absolute position) or None if no match
        """
        earliest_match = None
        earliest_format = None
        earliest_pos = len(text)
        
        # Check each pattern to find the earliest match
        for pattern, formatting in cls.FORMAT_PATTERNS:
            match = re.search(pattern, text[current_pos:])
            if match:
                absolute_pos = current_pos + match.start()
                if absolute_pos < earliest_pos:
                    earliest_match = match
                    earliest_format = formatting
                    earliest_pos = absolute_pos
        
        if earliest_match is None:
            return None
            
        return earliest_match, earliest_format, earliest_pos
    
    @classmethod
    def _process_formatted_segment(cls, match: re.Match, formatting: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """
        Process a formatted segment from a regex match.
        
        Args:
            match: The regex match object
            formatting: The formatting to apply
            
        Returns:
            Tuple of (content, formatting)
        """
        if 'highlight' in formatting:
            color = match.group(1)
            content = match.group(2)
            
            valid_colors = [
                "default", "gray", "brown", "orange", "yellow", "green", "blue", 
                "purple", "pink", "red", "gray_background", "brown_background", 
                "orange_background", "yellow_background", "green_background", 
                "blue_background", "purple_background", "pink_background", "red_background"
            ]
            
            if color not in valid_colors:
                if not color.endswith("_background"):
                    color = f"{color}_background"
                
                if color not in valid_colors:
                    color = "yellow_background"
            
            return (content, {'color': color})
        
        # Handle default highlighting (yellow)
        elif 'highlight_default' in formatting:
            content = match.group(1)
            return (content, {'color': 'yellow_background'})
        
        elif 'link' in formatting:
            content = match.group(1)
            url = match.group(2)
            return (content, {'url': url})
        
        else:
            content = match.group(1)
            return (content, formatting)
        
    
class ToggleContentProcessor:
    """Helper class to process content that should be nested inside toggle blocks."""
    
    @staticmethod
    def process_toggle_content(markdown_text: str, converter: 'MarkdownToNotionConverter') -> List[Dict[str, Any]]:
        """
        Process markdown text to identify toggle blocks and their nested content.
        
        Args:
            markdown_text: Markdown text to process
            converter: Instance of MarkdownToNotionConverter to use for processing inner content
            
        Returns:
            List of blocks with properly nested content
        """
        lines = markdown_text.split('\n')
        result_blocks = []
        i = 0
        
        toggle_parser = next((p for p in converter.element_parsers 
                             if isinstance(p, ToggleParser)), None)
        
        if not toggle_parser:
            return converter._convert_without_toggles(markdown_text)
        
        while i < len(lines):
            line = lines[i].rstrip()
            
            if toggle_parser.match(line):
                toggle_block = toggle_parser.parse(line)
                
                nested_content = []
                j = i + 1
                while j < len(lines):
                    next_line = lines[j]
                    
                    if (toggle_parser.match(next_line) or 
                        (next_line.strip() and not next_line.startswith('  '))):
                        break
                    
                    if next_line.startswith('  '):
                        nested_content.append(next_line[2:])
                    else:
                        nested_content.append(next_line)
                    
                    j += 1
                
                if nested_content:
                    nested_text = '\n'.join(nested_content)
                    child_blocks = converter._convert_without_toggles(nested_text)
                    if child_blocks:
                        toggle_block["toggle"]["children"] = child_blocks
                
                result_blocks.append(toggle_block)
                i = j  # Skip processed lines
            else:
                regular_content = []
                start_i = i
                
                while i < len(lines) and not toggle_parser.match(lines[i]):
                    regular_content.append(lines[i])
                    i += 1
                
                # Process regular content
                if regular_content:
                    regular_text = '\n'.join(regular_content)
                    regular_blocks = converter._convert_without_toggles(regular_text)
                    result_blocks.extend(regular_blocks)
        
        return result_blocks