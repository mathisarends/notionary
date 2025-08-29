from __future__ import annotations

from typing import Optional
from notionary.markdown.markdown_node import MarkdownNode


class ColumnMarkdownNode(MarkdownNode):
    """
    Programmatic interface for creating a single Markdown column block
    with nested content and optional width ratio.

    Example:
        ::: column
        # Column Title

        Some content here
        :::

        ::: column 0.7
        # Wide Column (70%)

        This column takes 70% width
        :::
    """

    def __init__(
        self, children: list[MarkdownNode], width_ratio: Optional[float] = None
    ):
        self.children = children
        self.width_ratio = width_ratio

    def to_markdown(self) -> str:
        # Start tag with optional width ratio
        if self.width_ratio is not None:
            start_tag = f"::: column {self.width_ratio}"
        else:
            start_tag = "::: column"

        if not self.children:
            return f"{start_tag}\n:::"

        # Convert children to markdown
        content_parts = [child.to_markdown() for child in self.children]
        content_text = "\n\n".join(content_parts)

        return f"{start_tag}\n{content_text}\n:::"
