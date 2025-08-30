from typing import Optional

from notionary.blocks.markdown.markdown_node import MarkdownNode


class TableOfContentsMarkdownNode(MarkdownNode):
    """
    Enhanced Table of Contents node with Pydantic integration.
    Programmatic interface for creating Markdown table of contents blocks.
    Example:
    [toc]
    [toc](blue)
    [toc](blue_background)
    """

    color: Optional[str] = "default"

    def to_markdown(self) -> str:
        if self.color == "default":
            return "[toc]"
        return f"[toc]({self.color})"
