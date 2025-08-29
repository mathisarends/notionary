from __future__ import annotations

from notionary.markdown.markdown_node import MarkdownNode


class NumberedListMarkdownNode(MarkdownNode):
    """
    Programmatic interface for creating Markdown numbered list items.
    Example:
    1. First step
    2. Second step
    3. Third step
    """

    def __init__(self, texts: list[str]):
        self.texts = texts

    def to_markdown(self) -> str:
        return "\n".join(f"{i + 1}. {text}" for i, text in enumerate(self.texts))
