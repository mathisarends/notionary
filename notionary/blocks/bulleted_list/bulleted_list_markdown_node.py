from __future__ import annotations

from notionary.markdown.markdown_node import MarkdownNode


class BulletedListMarkdownNode(MarkdownNode):
    """
    Enhanced BulletedList node with Pydantic integration.
    Programmatic interface for creating Markdown bulleted list items.
    Example:
    - First item
    - Second item
    - Third item
    """
    texts: list[str]

    def to_markdown(self) -> str:
        result = []
        for text in self.texts:
            result.append(f"- {text}")
        return "\n".join(result)
