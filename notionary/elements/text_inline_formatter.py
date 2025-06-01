from typing import Dict, Any, List, Tuple
import re

from notionary.prompting.element_prompt_content import (
    ElementPromptBuilder,
    ElementPromptContent,
)


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

            if "link" in earliest_format:
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
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        """
        Returns structured LLM prompt metadata for inline formatting.
        """
        return (
            ElementPromptBuilder()
            .with_description(
                "Inline formatting can be used within most block types to style your text. You can combine multiple formatting options."
            )
            .with_usage_guidelines(
                "Use inline formatting to highlight important words, provide emphasis, show code or paths, or add hyperlinks. "
                "This helps create visual hierarchy and improves readability."
            )
            .with_syntax(
                "**bold**, *italic*, `code`, ~~strikethrough~~, __underline__, [text](url)"
            )
            .with_examples(
                [
                    "This text has a **bold** word.",
                    "This text has an *italic* word.",
                    "This text has `code` formatting.",
                    "This text has ~~strikethrough~~ formatting.",
                    "This text has __underlined__ formatting.",
                    "This has a [hyperlink](https://example.com).",
                    "You can **combine *different* formatting** styles.",
                ]
            )
            .build()
        )
