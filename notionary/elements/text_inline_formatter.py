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
        (r"\*\*(.+?)\*\*", {"bold": True}),
        (r"\*(.+?)\*", {"italic": True}),
        (r"_(.+?)_", {"italic": True}),
        (r"__(.+?)__", {"underline": True}),
        (r"~~(.+?)~~", {"strikethrough": True}),
        (r"`(.+?)`", {"code": True}),
        (r"\[(.+?)\]\((.+?)\)", {"link": True}),
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
    def _split_text_into_segments(
        cls, text: str, format_patterns: List[Tuple]
    ) -> List[Dict[str, Any]]:
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
                segments.append(
                    cls._create_text_element(remaining_text[:earliest_pos], {})
                )

            elif "link" in earliest_format:
                content = earliest_match.group(1)
                url = earliest_match.group(2)
                segments.append(cls._create_link_element(content, url))

            else:
                content = earliest_match.group(1)
                segments.append(cls._create_text_element(content, earliest_format))

            # Move past the processed segment
            remaining_text = remaining_text[
                earliest_pos + len(earliest_match.group(0)) :
            ]

        return segments

    @classmethod
    def _create_text_element(
        cls, text: str, formatting: Dict[str, Any]
    ) -> Dict[str, Any]:
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
            if key == "color":
                annotations["color"] = value
            elif key in annotations:
                annotations[key] = value

        return {
            "type": "text",
            "text": {"content": text},
            "annotations": annotations,
            "plain_text": text,
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
            "text": {"content": text, "link": {"url": url}},
            "annotations": cls._default_annotations(),
            "plain_text": text,
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
            "color": "default",
        }

    @classmethod 
    def get_llm_prompt_content(cls) -> Dict[str, Any]: 
        """ 
        Returns information about inline text formatting capabilities for LLM prompts. 
        """
        return { 
            "description": "Proper typography is ESSENTIAL for readability and establishing visual hierarchy in text. Using Markdown formatting at strategic points demonstrably enhances comprehension and content scanability. It is MANDATORY to apply these formatting elements consistently and thoughtfully throughout all content.", 
            "syntax": [ 
                "**text** - Bold for key concepts, important terms, and main headings", 
                "*text* or _text_ - Italics for emphasis, definitions, and specialized terminology", 
                "__text__ - Underlining for elements requiring special attention or calls to action", 
                "~~text~~ - Strikethrough for outdated or no longer applicable information", 
                "`text` - Inline code for technical terms, file paths, and code examples", 
                "[text](url) - Hyperlinks for cross-references and external resources", 
                "<!-- spacer --> - Creates vertical spacing between elements for improved readability", 
            ], 
            "examples": [ 
                "This is a **fundamental principle** with several *important nuances*.", 
                "The project's *vision* is to create software that feels *intuitive* and responds *elegantly* to user needs.", 
                "The term *cognitive load* refers to the mental effort required to process information.", 
                "Remember that *how* you present information is often as important as *what* you present.", 
                "This feature is ~~deprecated~~ as of version 2.0 and has been replaced by new methods.", 
                "Edit the `config.json` file to configure settings.", 
                "Check our [documentation](https://docs.example.com) for more details.", 
                "First paragraph content.\n\n<!-- spacer -->\n\nSecond paragraph with additional spacing above.", 
            ], 
            "guidelines": [ 
                "Use **bold** for the MOST important concepts that readers should immediately notice", 
                "Apply *italics* to emphasize key terms, introduce new concepts, or add subtle emphasis", 
                "Use *italics* for book titles, publication names, and foreign language terms", 
                "Combine formatting thoughtfully - for example: \"The **primary goal** is to create an *accessible* interface\"", 
                "Reserve `code formatting` exclusively for technical elements, commands, and syntax", 
                "Structure information with deliberate spacing and formatting to guide the reader's eye", 
                "Always maintain consistency in formatting conventions throughout documents", 
            ], 
        }
