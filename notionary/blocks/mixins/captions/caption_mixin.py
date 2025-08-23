from typing import Optional
import re
from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter


class CaptionMixin:
    """Mixin to add caption parsing functionality to block elements."""

    # Generic caption pattern - finds caption anywhere in text
    CAPTION_PATTERN = re.compile(r"\(caption:([^)]*)\)")

    @classmethod
    def extract_caption(cls, text: str) -> Optional[str]:
        """
        Extract caption text from anywhere in the input text.
        Returns only the caption content, preserving parentheses in content.
        """
        # Look for (caption: followed by content followed by )
        # Handle cases where caption content contains parentheses
        caption_start = text.find("(caption:")
        if caption_start == -1:
            return None

        # Find the matching closing parenthesis
        # Start after "(caption:"
        content_start = caption_start + 9  # len("(caption:")
        paren_count = 1
        pos = content_start

        while pos < len(text) and paren_count > 0:
            if text[pos] == "(":
                paren_count += 1
            elif text[pos] == ")":
                paren_count -= 1
            pos += 1

        if paren_count == 0:
            # Found matching closing parenthesis
            return text[content_start : pos - 1]

        return None

    @classmethod
    def remove_caption(cls, text: str) -> str:
        """
        Remove caption from text and return clean text.
        Uses the same balanced parentheses logic as extract_caption.
        """
        caption_start = text.find("(caption:")
        if caption_start == -1:
            return text.strip()

        # Find the matching closing parenthesis
        content_start = caption_start + 9  # len("(caption:")
        paren_count = 1
        pos = content_start

        while pos < len(text) and paren_count > 0:
            if text[pos] == "(":
                paren_count += 1
            elif text[pos] == ")":
                paren_count -= 1
            pos += 1

        if paren_count == 0:
            # Remove the entire caption including the outer parentheses
            return (text[:caption_start] + text[pos:]).strip()

        # Fallback to regex-based removal if balanced parsing fails
        return cls.CAPTION_PATTERN.sub("", text).strip()

    @classmethod
    def build_caption_rich_text(cls, caption_text: str) -> list[RichTextObject]:
        """Return caption as canonical rich text list (with annotations)."""
        if not caption_text:
            return []
        # IMPORTANT: use the same formatter used elsewhere in the app
        return [RichTextObject.for_caption(caption_text)]

    @classmethod
    def format_caption_for_markdown(cls, caption_list: list[RichTextObject]) -> str:
        """Convert rich text caption back to markdown format."""
        if not caption_list:
            return ""
        # Preserve markdown formatting (bold, italic, etc.)
        caption_text = TextInlineFormatter.extract_text_with_formatting(caption_list)
        return f"(caption:{caption_text})" if caption_text else ""
