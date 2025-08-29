from __future__ import annotations

from notionary.markdown.markdown_node import MarkdownNode


class BulletedListMarkdownNode(MarkdownNode):
    """
    Programmatic interface for creating Markdown bulleted list items.
    Example:
    - First item
    - Second item
    - Third item
    """

    def __init__(self, texts: list[str]):
        self.texts = texts

    def to_markdown(self) -> str:
        result = []
        for text in self.texts:
            result.append(f"- {text}")
        return "\n".join(result)
