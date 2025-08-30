from __future__ import annotations

from notionary.blocks.markdown.markdown_node import MarkdownNode


class ParagraphMarkdownNode(MarkdownNode):
    """
    Enhanced Paragraph node with Pydantic integration.
    Programmatic interface for creating Markdown paragraphs.
    Paragraphs are standard text without special block formatting.
    """

    text: str

    def to_markdown(self) -> str:
        return self.text
