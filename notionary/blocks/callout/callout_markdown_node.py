from __future__ import annotations

from typing import Optional
from pydantic import BaseModel
from notionary.blocks.markdown_node import MarkdownNode


class CalloutMarkdownBlockParams(BaseModel):
    text: str
    emoji: Optional[str] = None


class CalloutMarkdownNode(MarkdownNode):
    """
    Programmatic interface for creating Notion-style callout Markdown blocks.
    Example: !> [💡] This is a callout
    """

    def __init__(self, text: str, emoji: Optional[str] = None):
        self.text = text
        self.emoji = emoji or "💡"  # Default emoji

    @classmethod
    def from_params(cls, params: CalloutMarkdownBlockParams) -> CalloutMarkdownNode:
        return cls(text=params.text, emoji=params.emoji)

    def to_markdown(self) -> str:
        if self.emoji and self.emoji != "💡":
            return f"!> [{self.emoji}] {self.text}"
        else:
            return f"!> [💡] {self.text}"
