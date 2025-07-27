from __future__ import annotations

from typing import Optional
from pydantic import BaseModel
from notionary.blocks.markdown_node import MarkdownNode


class QuoteMarkdownBlockParams(BaseModel):
    text: str
    author: Optional[str] = None


class QuoteMarkdownNode(MarkdownNode):
    """
    Programmatic interface for creating Notion-style quote blocks.
    Example: [quote](This is a quote "Author Name")
    """

    def __init__(self, text: str, author: Optional[str] = None):
        self.text = text
        self.author = author

    @classmethod
    def from_params(cls, params: QuoteMarkdownBlockParams) -> QuoteMarkdownNode:
        return cls(text=params.text, author=params.author)

    def to_markdown(self) -> str:
        if self.author:
            return f'[quote]({self.text} "{self.author}")'
        return f"[quote]({self.text})"
