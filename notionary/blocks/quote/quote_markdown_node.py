from __future__ import annotations

from notionary.blocks.markdown.markdown_node import MarkdownNode


class QuoteMarkdownNode(MarkdownNode):
    """
    Enhanced Quote node with Pydantic integration.
    Programmatic interface for creating Notion-style quote blocks.
    Example: > This is a quote
    """

    text: str

    def to_markdown(self) -> str:
        return f"> {self.text}"
