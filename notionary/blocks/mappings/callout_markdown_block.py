from typing import Optional
from notionary.blocks.mappings.markdown_node import MarkdownNode


class CalloutMarkdownBlock(MarkdownNode):
    """
    Programmatic interface for creating Notion-style callout Markdown blocks.
    Example: !> [💡] This is a callout
    """

    def __init__(self, text: str, emoji: Optional[str] = None):
        self.text = text
        self.emoji = emoji or "💡"  # Default emoji

    def to_markdown(self) -> str:
        # Wenn Emoji nicht gesetzt oder Standard: Ohne Emoji explizit
        if self.emoji and self.emoji != "💡":
            return f"!> [{self.emoji}] {self.text}"
        else:
            # Standard-Callout, Emoji kann weggelassen oder gesetzt werden
            return f"!> [💡] {self.text}"
