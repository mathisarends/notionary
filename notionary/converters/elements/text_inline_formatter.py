from typing import Dict, Any, List, Tuple
import re

class TextInlineFormatter:
    """
    Handles conversion between Markdown inline formatting and Notion rich text elements.
    
    Supports various formatting options:
    - Bold: **text**
    - Italic: *text* or _text_
    - Underline: __text__
    - Strikethrough: ~~text~~
    - Code: `text`
    - Links: [text](url)
    - Highlights: ==text== (default yellow) or ==color:text== (custom color)
    """
    
    # Format patterns for matching Markdown formatting
    FORMAT_PATTERNS = [
        (r'\*\*(.+?)\*\*', {'bold': True}),
        (r'\*(.+?)\*', {'italic': True}),
        (r'_(.+?)_', {'italic': True}),
        (r'__(.+?)__', {'underline': True}),
        (r'~~(.+?)~~', {'strikethrough': True}),
        (r'`(.+?)`', {'code': True}),
        (r'\[(.+?)\]\((.+?)\)', {'link': True}),
        (r'==([a-z_]+):(.+?)==', {'highlight': True}),
        (r'==(.+?)==', {'highlight_default': True}),
    ]
    
    # Valid colors for highlighting
    VALID_COLORS = [
        "default", "gray", "brown", "orange", "yellow", "green", "blue", 
        "purple", "pink", "red", "gray_background", "brown_background", 
        "orange_background", "yellow_background", "green_background", 
        "blue_background", "purple_background", "pink_background", "red_background"
    ]
    
    @classmethod
    def parse_inline_formatting(cls, text: str) -> List[Dict[str, Any]]:
        """
        Parse inline text formatting into Notion rich_text format.
        
        Args:
            text: Markdown text with inline formatting
            
        Returns:
            List of Notion rich_text objects
        """
        if not text:
            return []
        
        return cls._split_text_into_segments(text, cls.FORMAT_PATTERNS)
    
    @classmethod
    def _split_text_into_segments(cls, text: str, format_patterns: List[Tuple]) -> List[Dict[str, Any]]:
        """
        Split text into segments by formatting markers and convert to Notion rich_text format.
        
        Args:
            text: Text to split
            format_patterns: List of (regex pattern, formatting dict) tuples
            
        Returns:
            List of Notion rich_text objects
        """
        segments = []
        remaining_text = text
        
        while remaining_text:
            earliest_match = None
            earliest_format = None
            earliest_pos = len(remaining_text)
            
            # Find the earliest formatting marker
            for pattern, formatting in format_patterns:
                match = re.search(pattern, remaining_text)
                if match and match.start() < earliest_pos:
                    earliest_match = match
                    earliest_format = formatting
                    earliest_pos = match.start()
            
            if earliest_match is None:
                if remaining_text:
                    segments.append(cls._create_text_element(remaining_text, {}))
                break
            
            if earliest_pos > 0:
                segments.append(cls._create_text_element(remaining_text[:earliest_pos], {}))
            
            if 'highlight' in earliest_format:
                color = earliest_match.group(1)
                content = earliest_match.group(2)
                
                if color not in cls.VALID_COLORS:
                    if not color.endswith("_background"):
                        color = f"{color}_background"
                    
                    if color not in cls.VALID_COLORS:
                        color = "yellow_background"
                
                segments.append(cls._create_text_element(content, {'color': color}))
            
            elif 'highlight_default' in earliest_format:
                content = earliest_match.group(1)
                segments.append(cls._create_text_element(content, {'color': 'yellow_background'}))
            
            elif 'link' in earliest_format:
                content = earliest_match.group(1)
                url = earliest_match.group(2)
                segments.append(cls._create_link_element(content, url))
            
            else:
                content = earliest_match.group(1)
                segments.append(cls._create_text_element(content, earliest_format))
            
            # Move past the processed segment
            remaining_text = remaining_text[earliest_pos + len(earliest_match.group(0)):]
            
        return segments
    
    @classmethod
    def _create_text_element(cls, text: str, formatting: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a Notion text element with formatting.
        
        Args:
            text: The text content
            formatting: Dictionary of formatting options
            
        Returns:
            Notion rich_text element
        """
        annotations = cls._default_annotations()
        
        # Apply formatting
        for key, value in formatting.items():
            if key == 'color':
                annotations['color'] = value
            elif key in annotations:
                annotations[key] = value
        
        return {
            "type": "text",
            "text": {"content": text},
            "annotations": annotations,
            "plain_text": text
        }
    
    @classmethod
    def _create_link_element(cls, text: str, url: str) -> Dict[str, Any]:
        """
        Create a Notion link element.
        
        Args:
            text: The link text
            url: The URL
            
        Returns:
            Notion rich_text element with link
        """
        return {
            "type": "text",
            "text": {
                "content": text,
                "link": {"url": url}
            },
            "annotations": cls._default_annotations(),
            "plain_text": text
        }
    
    @classmethod
    def extract_text_with_formatting(cls, rich_text: List[Dict[str, Any]]) -> str:
        """
        Convert Notion rich_text elements back to Markdown formatted text.
        
        Args:
            rich_text: List of Notion rich_text elements
            
        Returns:
            Markdown formatted text
        """
        formatted_parts = []

        for text_obj in rich_text:
            # Fallback: If plain_text is missing, use text['content']
            content = text_obj.get("plain_text")
            if content is None:
                content = text_obj.get("text", {}).get("content", "")

            annotations = text_obj.get("annotations", {})

            if annotations.get("code", False):
                content = f"`{content}`"
            if annotations.get("strikethrough", False):
                content = f"~~{content}~~"
            if annotations.get("underline", False):
                content = f"__{content}__"
            if annotations.get("italic", False):
                content = f"*{content}*"
            if annotations.get("bold", False):
                content = f"**{content}**"

            color = annotations.get("color", "default")
            if color != "default":
                content = f"=={color.replace('_background', '')}:{content}=="

            text_data = text_obj.get("text", {})
            link_data = text_data.get("link")
            if link_data:
                url = link_data.get("url", "")
                content = f"[{content}]({url})"

            formatted_parts.append(content)

        return "".join(formatted_parts)
    
    @classmethod
    def _default_annotations(cls) -> Dict[str, bool]:
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
    
    @classmethod
    def get_llm_prompt_content(cls) -> Dict[str, Any]:
        """
        Returns information about inline text formatting capabilities for LLM prompts.
        
        This method provides documentation about supported inline formatting options
        that can be used across all block elements.
        
        Returns:
            A dictionary with descriptions, syntax examples, and usage guidelines
        """
        return {
            "description": "Standard Markdown formatting is supported in all text blocks. Additionally, a custom highlight syntax is available for emphasizing important information. To create vertical spacing between elements, use the special spacer tag.",
            
            "syntax": [
                "**text** - Bold text",
                "*text* or _text_ - Italic text",
                "__text__ - Underlined text",
                "~~text~~ - Strikethrough text",
                "`text` - Inline code",
                "[text](url) - Link",
                "==text== - Default highlight (yellow background)",
                "==color:text== - Colored highlight (e.g., ==red:warning==)",
                "<!-- spacer --> - Creates vertical spacing between elements"
            ],
            
            "examples": [
                "This is a **bold** statement with some *italic* words.",
                "This feature is ~~deprecated~~ as of version 2.0.",
                "Edit the `config.json` file to configure settings.",
                "Check our [documentation](https://docs.example.com) for more details.",
                "==This is an important note== that you should remember.",
                "==red:Warning:== This action cannot be undone.",
                "==blue:Note:== Common colors include red, blue, green, yellow, purple.",
                "First paragraph content.\n\n<!-- spacer -->\n\nSecond paragraph with additional spacing above."
            ],
            
            "highlight_usage": "The highlight syntax (==text== and ==color:text==) should be used to emphasize important information, warnings, notes, or other content that needs to stand out. This is particularly useful for making content more scannable at a glance.",
            
            "spacer_usage": "Use the <!-- spacer --> tag on its own line to create additional vertical spacing between elements. This is useful for improving readability by visually separating sections of content. Multiple spacer tags can be used for greater spacing."
        }
