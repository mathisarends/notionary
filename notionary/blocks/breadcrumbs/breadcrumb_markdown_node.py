from __future__ import annotations

from notionary.markdown.markdown_node import MarkdownNode


class BreadcrumbMarkdownNode(MarkdownNode):
    """
    Enhanced Breadcrumb node with Pydantic integration.
    Programmatic interface for creating Markdown breadcrumb blocks.
    Example:
    [breadcrumb]
    """

    def to_markdown(self) -> str:
        return "[breadcrumb]"
