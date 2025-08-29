from __future__ import annotations

from pydantic import BaseModel

from notionary.markdown.markdown_node import MarkdownNode



class BreadcrumbMarkdownNode(MarkdownNode):
    """
    Programmatic interface for creating Markdown breadcrumb blocks.
    Example:
    [breadcrumb]
    """

    def __init__(self):
        # No parameters needed for breadcrumb
        pass

    def to_markdown(self) -> str:
        return "[breadcrumb]"
