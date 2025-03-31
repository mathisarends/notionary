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
            HeadingParser(),
            BulletListParser(),
            NumberedListParser(),
            InlineCodeParser(),
            ParagraphParser()
        ]
    
    def convert(self, markdown_text: str) -> List[Dict[str, Any]]:
        """
        Convert markdown text to Notion API block format.
        
        Args:
            markdown_text: Markdown text to convert
            
        Returns:
            List of Notion block objects ready to be sent to the Notion API
        """
        if not markdown_text:
            return []
        
        # Get all segments with multi-line elements marked for special processing
        # This approach preserves the original order of content
        segments = self._split_with_multiline_markers(markdown_text)
        
        blocks = []
        
        # Process each segment in order
        for segment_type, segment_text in segments:
            if segment_type == "code_block":
                # If it's a code block, parse it directly
                code_parser = next((p for p in self.element_parsers if isinstance(p, CodeBlockParser)), None)
                if code_parser:
                    block = code_parser.parse(segment_text)
                    if block:
                        blocks.append(block)
            elif segment_text.strip():
                # Process text segments normally
                segment_blocks = self._process_text_segment(segment_text)
                blocks.extend(segment_blocks)
                    
        return blocks
    
    def _split_with_multiline_markers(self, text: str) -> List[Tuple[str, str]]:
        """
        Split text into segments, marking multi-line elements.
        
        Args:
            text: The markdown text
            
        Returns:
            List of tuples (segment_type, segment_text)
            where segment_type is either "text" or "code_block"
        """
        # Get multi-line parsers
        multiline_parsers = [p for p in self.element_parsers if p.is_multiline]
        
        # If no multi-line parsers, return the whole text as a text segment
        if not multiline_parsers:
            return [("text", text)]
        
        # Get code block parser
        code_parser = next((p for p in multiline_parsers if isinstance(p, CodeBlockParser)), None)
        if not code_parser or not code_parser.match(text):
            return [("text", text)]
        
        # Find all code blocks with their positions
        matches = code_parser.find_matches(text)
        if not matches:
            return [("text", text)]
        
        # Sort matches by start position to preserve order
        matches.sort(key=lambda m: m[0])
        
        segments = []
        last_end = 0
        
        for start, end, block in matches:
            if start > last_end:
                segments.append(("text", text[last_end:start]))
            
            segments.append(("code_block", text[start:end]))
            
            last_end = end
        
        if last_end < len(text):
            segments.append(("text", text[last_end:]))
        
        return segments
    
    def _process_text_segment(self, text: str) -> List[Dict[str, Any]]:
        """
        Process a text segment line by line to identify block types.
        
        Args:
            text: Text segment to process
            
        Returns:
            List of Notion blocks
        """
        segment_blocks = []
        paragraph_lines = []
        
        for line in text.split('\n'):
            # Empty line - process accumulated paragraph
            if not line.strip() and paragraph_lines:
                paragraph_text = '\n'.join(paragraph_lines)
                segment_blocks.append(ParagraphParser().parse(paragraph_text))
                paragraph_lines = []
                continue
                
            # Skip empty lines
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
            # If it's a special block but no paragraph lines, just add it
            elif block["type"] != "paragraph":
                segment_blocks.append(block)
            # If it's a paragraph, add to paragraph lines
            else:
                paragraph_lines.append(line)
        
        # Process any remaining paragraph lines
        if paragraph_lines:
            paragraph_text = '\n'.join(paragraph_lines)
            segment_blocks.append(ParagraphParser().parse(paragraph_text))
            
        return segment_blocks
    
    def _parse_line(self, line: str) -> Dict[str, Any]:
        """
        Parse a single line to determine its block type.
        
        Args:
            line: Text line to parse
            
        Returns:
            Notion block object
        """
        # Try each parser in order (skipping multi-line parsers and inline code parser)
        for parser in self.element_parsers:
            if parser.is_multiline or isinstance(parser, InlineCodeParser):
                continue
                
            if parser.match(line):
                block = parser.parse(line)
                if block:
                    return block
                    
        # This should never happen since we have a fallback parser
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
        
        Args:
            segment: (text, formatting) tuple
            
        Returns:
            Notion text element
        """
        text, formatting = segment
        
        if 'url' in formatting:
            return {
                "type": "text",
                "text": {
                    "content": text,
                    "link": {"url": formatting['url']}
                },
                "annotations": MarkdownToNotionConverter.default_annotations()
            }
            
        annotations = MarkdownToNotionConverter.default_annotations()
        annotations.update(formatting)
        
        return {
            "type": "text",
            "text": {"content": text},
            "annotations": annotations
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