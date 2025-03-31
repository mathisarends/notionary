import re
from typing import List, Dict, Any, Tuple, Optional
from abc import ABC, abstractmethod


class MarkdownElementParser(ABC):
    """Base class for parsing specific markdown elements."""
    
    @abstractmethod
    def match(self, text: str) -> bool:
        """Check if this parser can handle the given text."""
        pass
        
    @abstractmethod
    def parse(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse the text into a Notion block structure."""
        pass


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
    
    def parse(self, text: str) -> Tuple[Optional[Dict[str, Any]], int, int]:
        """
        Parse a code block into a Notion code block.
        
        Returns:
            Tuple containing:
            - The parsed block (or None if no match)
            - Start position of the match
            - End position of the match
        """
        match = self.pattern.search(text)
        if not match:
            return None, -1, -1
            
        language = match.group(1) or "plain text"
        content = match.group(2)
        
        # Remove trailing newline if present to avoid extra blank line
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
                        "annotations": MarkdownToNotionConverter._default_annotations()
                    }
                ],
                "language": language
            }
        }
        
        return block, match.start(), match.end()


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
        # Register element parsers in order of preference
        self.element_parsers = [
            HeadingParser(),
            BulletListParser(),
            NumberedListParser(),
            InlineCodeParser(),  # For inline code detection
            ParagraphParser()  # This should be last as it's the fallback
        ]
        
        # Special parser for code blocks that span multiple lines
        self.code_block_parser = CodeBlockParser()
    
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
            
        blocks = []
        
        # First, extract and handle code blocks separately
        segments = self._process_code_blocks(markdown_text, blocks)
        
        # Process each non-code text segment
        for segment in segments:
            if segment.strip():
                segment_blocks = self._process_text_segment(segment)
                blocks.extend(segment_blocks)
                    
        return blocks
    
    def _process_code_blocks(self, text: str, blocks: List[Dict[str, Any]]) -> List[str]:
        """
        Process and extract code blocks from the text.
        
        Args:
            text: The markdown text
            blocks: List to append code blocks to
            
        Returns:
            List of text segments without code blocks
        """
        if not self.code_block_parser.match(text):
            return [text]
            
        segments = []
        last_end = 0
        
        while True:
            block, start, end = self.code_block_parser.parse(text[last_end:])
            if start == -1:  # No more code blocks
                break
                
            # Adjust positions to account for offset
            start += last_end
            end += last_end
            
            # Add text before code block
            if start > last_end:
                segments.append(text[last_end:start])
            
            # Add the code block
            blocks.append(block)
            
            last_end = end
        
        # Add remaining text
        if last_end < len(text):
            segments.append(text[last_end:])
            
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
                
            # Try each parser to find a match
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
        # Try each parser in order (excluding InlineCodeParser which is for inline formatting)
        for parser in self.element_parsers:
            if isinstance(parser, InlineCodeParser):
                continue  # Skip inline code parser for block-level parsing
                
            if parser.match(line):
                block = parser.parse(line)
                if block:
                    return block
                    
        # This should never happen since we have a fallback parser
        return ParagraphParser().parse(line)
    
    @staticmethod
    def parse_inline_formatting(text: str) -> List[Dict[str, Any]]:
        """
        Parse inline text formatting (bold, italic, code, etc.)
        
        Args:
            text: Text to parse
            
        Returns:
            List of Notion rich_text objects
        """
        if not text:
            return []

        elements = []
        segments = MarkdownToNotionConverter._split_text_into_segments(text)
        
        for segment in segments:
            element = MarkdownToNotionConverter._create_text_element(segment)
            if element:
                elements.append(element)
                
        return elements
    
    @staticmethod
    def _split_text_into_segments(text: str) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Split text into segments by formatting markers.
        
        Args:
            text: Text to split
            
        Returns:
            List of (text, formatting) tuples
        """
        # Define format patterns with their corresponding annotation settings
        format_patterns = [
            (r'\*\*(.+?)\*\*', {'bold': True}),
            (r'\*(.+?)\*', {'italic': True}),
            (r'_(.+?)_', {'italic': True}),
            (r'__(.+?)__', {'underline': True}),
            (r'~~(.+?)~~', {'strikethrough': True}),
            (r'`(.+?)`', {'code': True}),  # Inline code
            (r'\[(.+?)\]\((.+?)\)', {'link': True}),
        ]
        
        segments = []
        current_pos = 0
        
        while current_pos < len(text):
            earliest_match = None
            earliest_format = None
            earliest_pos = len(text)
            
            # Find next formatting
            for pattern, formatting in format_patterns:
                match = re.search(pattern, text[current_pos:])
                if match and (current_pos + match.start()) < earliest_pos:
                    earliest_match = match
                    earliest_format = formatting
                    earliest_pos = current_pos + match.start()
            
            if not earliest_match:
                # Add remaining text as plain segment
                if current_pos < len(text):
                    segments.append((text[current_pos:], {}))
                break
                
            # Add text before formatting as plain segment
            if earliest_pos > current_pos:
                segments.append((text[current_pos:earliest_pos], {}))
            
            # Add formatted segment
            content = earliest_match.group(1)
            if 'link' in earliest_format:
                url = earliest_match.group(2)
                segments.append((content, {'url': url}))
            else:
                segments.append((content, earliest_format))
            
            current_pos = earliest_pos + len(earliest_match.group(0))
            
        return segments
    
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
                "annotations": MarkdownToNotionConverter._default_annotations()
            }
            
        annotations = MarkdownToNotionConverter._default_annotations()
        annotations.update(formatting)
        
        return {
            "type": "text",
            "text": {"content": text},
            "annotations": annotations
        }
    
    @staticmethod
    def _default_annotations() -> Dict[str, bool]:
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