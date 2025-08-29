from __future__ import annotations
from notionary.markdown.markdown_node import MarkdownNode


class DividerMarkdownNode(MarkdownNode):
    """
    Programmatic interface for creating Markdown divider lines (---).
    """

    def __init__(self):
        pass  # Keine Attribute notwendig

    def to_markdown(self) -> str:
        return "---"
