from __future__ import annotations

from typing import Optional
from notionary.markdown.markdown_node import MarkdownNode

class CalloutMarkdownNode(MarkdownNode):
    """
    Programmatic interface for creating Notion-style callout Markdown blocks.
    Example: [callout](This is important "⚠️")
    """

    def __init__(self, text: str, emoji: Optional[str] = None):
        self.text = text
        self.emoji = emoji


    def to_markdown(self) -> str:
        if self.emoji and self.emoji != "💡":
            return f'[callout]({self.text} "{self.emoji}")'
        else:
            return f"[callout]({self.text})"
