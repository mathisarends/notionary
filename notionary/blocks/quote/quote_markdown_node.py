from __future__ import annotations

from notionary.markdown.markdown_node import MarkdownNode


class QuoteMarkdownNode(MarkdownNode):
    """
    Programmatic interface for creating Notion-style quote blocks.
    Example: > This is a quote
    """

    def __init__(self, text: str):
        self.text = text

    def to_markdown(self) -> str:
        return f"> {self.text}"
