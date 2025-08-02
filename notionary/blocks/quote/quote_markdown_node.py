from __future__ import annotations

from pydantic import BaseModel
from notionary.blocks.markdown_node import MarkdownNode


class QuoteMarkdownBlockParams(BaseModel):
    text: str


class QuoteMarkdownNode(MarkdownNode):
    """
    Programmatic interface for creating Notion-style quote blocks.
    Example: [quote](This is a quote)
    """

    def __init__(self, text: str):
        self.text = text

    @classmethod
    def from_params(cls, params: QuoteMarkdownBlockParams) -> QuoteMarkdownNode:
        return cls(text=params.text)

    def to_markdown(self) -> str:
        return f"[quote]({self.text})"
