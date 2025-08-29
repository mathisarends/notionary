from __future__ import annotations

from notionary.markdown.markdown_node import MarkdownNode


class ParagraphMarkdownNode(MarkdownNode):
    """
    Programmatic interface for creating Markdown paragraphs.
    Paragraphs are standard text without special block formatting.
    """

    def __init__(self, text: str):
        self.text = text

    def to_markdown(self) -> str:
        return self.text
