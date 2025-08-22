# caption_mixin.py
from typing import Optional, Tuple
import re
from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter


class CaptionMixin:
    """Mixin to add caption parsing functionality to block elements."""

    # Generic caption pattern - finds caption anywhere in text
    CAPTION_PATTERN = re.compile(r"\(caption:\s*(.+?)\)")

    @classmethod
    def extract_caption(cls, text: str) -> Optional[str]:
        """
        Extract caption text from anywhere in the input text.
        Returns only the caption content, not a tuple.
        """
        m = cls.CAPTION_PATTERN.search(text)
        if not m:
            return None
        return m.group(1).strip()

    @classmethod
    def remove_caption(cls, text: str) -> str:
        """
        Remove caption from text and return clean text.
        Separate method for flexibility.
        """
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
