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
            position += len(lines[i]) + 1  # +1 für Zeilenumbruch
        return position

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
            TableParser(),  # The improved TableParser
            HeadingParser(),
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
        Find all multiline elements like tables and code blocks.
        """
        multiline_parsers = [p for p in self.element_parsers if p.is_multiline]
        special_matches = []
        
        for parser in multiline_parsers:
            if not hasattr(parser, 'find_matches') or not parser.match(markdown_text):
                continue
                
            try:
                matches = parser.find_matches(markdown_text)
                parser_type = "table" if isinstance(parser, TableParser) else "code_block"
                
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
            elif segment_type in ["code_block", "table"]:
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
        """Parse inline text formatting (bold, italic, code, etc.)"""
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
        annotations.update(formatting)
        
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
        
        
class TextFormattingParser:
    """
    Helper class for parsing inline text formatting in markdown.
    This class breaks down the complex task of parsing inline formatting
    into smaller, more manageable methods.
    """
    
    FORMAT_PATTERNS = [
        (r'\*\*(.+?)\*\*', {'bold': True}),
        (r'\*(.+?)\*', {'italic': True}),
        (r'_(.+?)_', {'italic': True}),
        (r'__(.+?)__', {'underline': True}),
        (r'~~(.+?)~~', {'strikethrough': True}),
        (r'`(.+?)`', {'code': True}),  # Inline code
        (r'\[(.+?)\]\((.+?)\)', {'link': True}),
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
        content = match.group(1)
        
        if 'link' in formatting:
            url = match.group(2)
            return (content, {'url': url})
        
        return (content, formatting)