from __future__ import annotations

from typing import Optional
from notionary.markdown.markdown_node import MarkdownNode


class TableOfContentsMarkdownNode(MarkdownNode):
    """
    Programmatic interface for creating Markdown table of contents blocks.
    Example:
    [toc]
    [toc](blue)
    [toc](blue_background)
    """

    def __init__(self, color: Optional[str] = "default"):
        self.color = color or "default"

    def to_markdown(self) -> str:
        if self.color == "default":
            return "[toc]"
        return f"[toc]({self.color})"
