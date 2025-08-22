from typing import Optional


class CaptionMarkdownNodeMixin:
    """Mixin to add caption functionality to MarkdownNode classes."""

    @classmethod
    def append_caption_to_markdown(
        cls, base_markdown: str, caption: Optional[str]
    ) -> str:
        """
        Append caption to existing markdown if caption is present.
        Returns: base_markdown + "(caption:...)" or just base_markdown
        """
        if not caption:
            return base_markdown
        return f"{base_markdown}(caption:{caption})"

    @classmethod
    def format_caption_for_markdown(cls, caption: Optional[str]) -> str:
        """
        Format caption text for markdown output.
        Returns: "(caption:...)" or empty string
        """
        if not caption:
            return ""
        return f"(caption:{caption})"

    def has_caption(self) -> bool:
        """Check if this node has a caption."""
        return hasattr(self, "caption") and bool(getattr(self, "caption", None))
